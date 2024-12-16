import json
import os
import logging

import site
from time import process_time_ns
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from exceptiongroup import catch
from fastapi import APIRouter, Depends, Request
from httplib2 import Http
from httpx import HTTPError
from sympy import catalan
from src.plugins.auth.firebase import verify_firebase_token
from openai import OpenAI
from src.plugins.chat.schema import Analysis, ChatResponse
from src.plugins.kpi import service as kpi_service
from src.plugins.kpi import controller as kpi_controller
from src.plugins.machine import repository as machine_repository
from http.client import HTTPResponse
from src.plugins.kpi.schema import KPIOverview
import warnings
warnings.filterwarnings("ignore")
from .service import cost_prediction, utilization_analysis, energy_efficency_analysis

# Run the cost prediction, utilization and energy efficiency analysis
print("Starting the ml analysis...")
print("Running cost prediction...")
cost_prediction_for_category,pdf_path = cost_prediction()
print("Cost prediction done")
print("----------------------")
print("Run utilization and energy efficiency analysis...")
utilization = utilization_analysis()
energy_efficiency = energy_efficency_analysis()
print("Analysis done")
print("----------------------")

prompt = """You are a specialized AI assistant that mocks a Retrieval-Augmented Generation (RAG) system for an industrial domain. Your primary responsibilities are:

1. **Answer General Questions:** Respond politely and provide answers only if the question is within the boundaries of the provided knowledge base (KB), which includes:
    - A list of Key Performance Indicators (KPIs) available.
    - A list of machines available.
    - The average daily cost for the next month for each machine category.
    - The utilization for each machine.
    - The energy efficiency for each machine.
If the information required to answer is not in the KB, explicitly state:
   "I'm sorry, but I cannot answer this question as it is not covered in the knowledge base."

2. **Generate New KPI Formulas:**
   - Generate new Key Performance Indicators (KPIs) **only if the query explicitly contains keywords like 'create' 'generate' 'design', 'suggest' or similar.** If the query does not contain such keywords, do not generate a KPI and treat the query as a general question.
   - Return the KPI generation response **strictly** in the following JSON format, with no additional text:

{
  "KPIs": [
    {
      "name": "<KPI Name>",
      "type": "<Type of KPI>",
      "description": "<Brief description of the new KPI>",
      "unit_of_measure": "<Unit of measure of the new KPI>",
      "formula": "<Mathematical formula to calculate the new KPI using already available KPIs>"
    }
  ]
}

   - Only generate formulas using the KPIs explicitly provided in the KB. Do not compute values for KPIs, as you are not currently capable of doing so.

3. **Respond to Specific Topics:** You can answer questions specifically about:
   - **Cost Prediction:** Provide the average daily cost (in EUR/kWh) for each machine category, based on predictions available in the KB.
   - **Utilization Analysis:** Explain the utilization metric as a percentage:
     Utilization = (working_time / (working_time + idle_time + offline_time)) × 100
   - **Energy Efficiency Analysis:** Explain the efficiency metric as a ratio between 0 and 1:
     Energy Efficiency = consumption_idle / (consumption_idle + consumption_working)

4. **Key Rules for Responses:**
   - **Strict Adherence to Knowledge Base:** Do not invent facts or provide answers outside the KB.
   - **JSON-Only Responses for KPIs:** Ensure that responses to KPI generation requests are purely JSON, without any introductory or explanatory text.
   - **Politeness for Unsupported Queries:** Always respond politely when declining a query.

By following these guidelines, you will effectively simulate a RAG system for industrial applications.
"""

# Prompt for kpi computation
# and computation
#If the question is a KPI computation, try to compute the KPI based on the available KPIs and return a response in the JSON format below:
#{
#    "ComputeKPIs": [
#        {
#            "kpi_id": "<KPI ID>", # You can get it from the Knowledge base
#            "kpi_name": "<KPI Name>", # You can get it from the Knowledge base
#            "category": "<Category of the machines>", # If not provided set it to None
#            "start_date": "<Start date>", # Format: YYYY-MM-DD 00:00:00 if not provided use 2024-09-30 00:00:00
#            "end_date": "<End date>", # Format: YYYY-MM-DD 00:00:00 if not provided use 2024-10-14 00:00:00
#            "granularity_days": "<Granularity days>", # Possible values: 1, 7, 30
#            "granularity_op": "<Granularity operation>" # Possible values: sum, avg, min, max
#        },
#        ...
#    ]
#}

logger = logger = logging.getLogger('uvicorn.error')
API_VERSION = os.getenv("VERSION")
DEBUG = os.getenv("DEBUG")

router = APIRouter(prefix=f"/api/{API_VERSION}/chat", tags=["Chat"])

@router.post("/", status_code=200, summary="Get chat response")
async def getChatResponse(
    request: Request,
    site_id: int,
    query: str,
    user=Depends(verify_firebase_token)
):
    """
    This endpoint is used to get a response from the chatbot based on the query provided.

    Args:
    - site_id: int - The site id
    - query: str - The query to send to the chatbot

    Returns:
    - str: The response from the chatbot
    """
    # get kb
    all_kpi: List[KPIOverview] = await kpi_service.listKPIs(site=site_id, request=request)

    all_machines = await machine_repository.get_all(request)
    # get only the machine names
    all_machines = [(machine.name, machine.category) for machine in all_machines]

    try:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system", "content": prompt},
                {"role": "system", "content": "Consider that your knowledge base is composed by the following KPIs:"+str(all_kpi)+" and the following machines:"+str(all_machines)+ " and the average daily cost for the next month for each machine category: "+str(cost_prediction_for_category)+" and the utilization analysis for each machine is:"+str(utilization)+ " and the energy efficiency analysis for each machine is:"+str(energy_efficiency)},
                {"role": "user", "content": query}
            ]
        )
        response = completion.choices[0].message.content
        if response.startswith("{") and response.endswith("}"):
            # json response from chat
            json_kpi = json.loads(response)
            print(json_kpi)
            if json_kpi.get("KPIs"):
                # create kpi
                created_kpis = []
                for kpi in json_kpi["KPIs"]:
                    try:
                        kpi_tmp = await kpi_service.createKPI(
                            request,
                            kpi["name"],
                            kpi["type"],
                            kpi["description"],
                            kpi["unit_of_measure"],
                            kpi["formula"],
                            user.uid
                        )
                        created_kpis.append(kpi_tmp.name)
                    except Exception as e:
                        print(f"Error creating KPI: {e}")
                created_kpis = ", ".join(created_kpis)
                if len(created_kpis) > 0:
                    return {f'Successfully created KPIs: {created_kpis}'}
                else:
                    return {'Impossible to create KPIs'}
            #elif json_kpi.get("ComputeKPIs"):
            #    # compute kpi
            #    computed_kpis = {}
            #    for kpi in json_kpi["ComputeKPIs"]:
            #        print(kpi)
            #        try:
            #            kpi_tmp = await kpi_controller.computeKPIBySite(
            #                request,
            #                site_id,
            #                kpi["kpi_id"],
            #                kpi["start_date"],
            #                kpi["end_date"],
            #                kpi["granularity_op"],
            #                kpi["granularity_days"],
            #                kpi["category"] if kpi.get("category") else None,
            #                user
            #            )
            #            computed_kpis[kpi["kpi_name"]] = kpi_tmp.data
            #        except Exception as e:
            #            print(f"Error computing KPI: {e}")
            #    print(computed_kpis)
            #    computed_kpis = json.dumps(computed_kpis)
            #    if len(computed_kpis) > 0:
            #        return {f'Successfully computed KPIs: {computed_kpis}'}
            #    else:
            #        return {'Impossible to compute KPIs'}
        else:
            # normal response from chat
            return response
    except Exception as e:
        print(f"Error getting chat response: {e}")
        return ChatResponse(success=False, data=None, message=f"Error getting chat response: {str(e)}")

# get analysis results and predictions
@router.get("/", status_code=200, summary="Get ml analysis results")
async def getAnalysis(
    request: Request,
    user=Depends(verify_firebase_token)
):
    """
    This endpoint is used to get the analysis results from the ml analysis.
    Returns:
    - dict: The analysis results
    """
    try:
        for k,v in cost_prediction_for_category.items():
            cost_prediction_for_category[k] = str(v)

        return ChatResponse(
            success=True,
            data=Analysis(
                cost_prediction = cost_prediction_for_category,
                utilization = utilization.to_dict(),
                energy_efficiency = energy_efficiency.to_dict()
            ),
            message="Analysis results retrieved successfully")

    except Exception as e:
        print(f"Error getting analysis results: {e}")
        return ChatResponse(success=False, data=None, message=f"Error getting analysis results: {str(e)}")