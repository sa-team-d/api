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
from sympy import catalan
from src.plugins.auth.firebase import verify_firebase_token
from openai import OpenAI
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

prompt = """
You are a specialized assistant that mocks a RAG system for a Industry. Your job is to only replay to general questions relative to the known Knowledge base and KPI generation or suggestions based on the available KPI.

If the question is a general question, act politely and provide the answer if it is in the knowledge base. If the question is not in the knowledge base, provide a polite response that the question is not in the knowledge base.

If the question is a KPI generation, try to generate a new KPI formula and return a response in the JSON format below:

{
  "KPIs": [
    {
      "name": "<KPI Name>",
      "type": "<Type of KPI>",
      "description": "<Brief description of the new KPI>",
      "unit_of_measure": "<Unit of measure of the new KPI>",
      "formula": "<Mathematical formula to calculate the new KPI using already available KPIs>"
    },
    ...
  ]
}

You can only generate a new KPI formula using the already available KPIs. You are not able to compute the value of a KPI up to know, in future you will be able to do it.

You can also answer to question related to the cost prediction for each machine category. The average daily cost for the next month for each machine category is provided in the Knowledge base and the unit of measure is in EUR/kWh.

You can also answer to question related to the utilization analysis and energy efficiency analysis. The unit of measure for the utilization analysis is in % of working_time / (working_time + idle_time + offline_time) and for the energy efficiency is a ratio between 0 and 1 of consumption_idle / (consumption_idle + consumption_working). The results are provided in the Knowledge base.

In case of a json response, make sure to return only a valid JSON response with the KPIs generated, without any other text. First and last character should be curly braces.

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
                {"role": "system", "content": "Consider that your knowledge base is composed by the following KPIs:"+str(all_kpi)+" and the following machines:"+str(all_machines)},
                {"role": "system", "content": "Consider that the average daily cost for the next month for each machine category is:"+str(cost_prediction_for_category)},
                {"role": "system", "content": "Consider that the utilization analysis for each machine is:"+str(utilization)},
                {"role": "system", "content": "Consider that the energy efficiency analysis for each machine is:"+str(energy_efficiency)},
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
        return HTTPResponse(status=500, reason="Error getting chat response")