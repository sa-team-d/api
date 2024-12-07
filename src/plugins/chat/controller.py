import json
import os
import logging

from typing import List, Optional
from datetime import datetime
from exceptiongroup import catch
from fastapi import APIRouter, Depends, Request
from httplib2 import Http
from sympy import catalan
from src.plugins.auth.firebase import verify_firebase_token
from openai import OpenAI
from src.plugins.kpi import service as kpi_service
from src.plugins.machine import repository as machine_repository
from http.client import HTTPResponse

from src.plugins.kpi.schema import KPIOverview

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

In case of a json response, make sure to return only a valid JSON response with the KPIs generated, without any other text.

"""

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
                {"role": "user", "content": query}
            ]
        )
        response = completion.choices[0].message.content
        if response.startswith("{") and response.endswith("}"):
            # json response from chat
            json_kpi = json.loads(response)
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
            return {f'Successfully created KPIs: {created_kpis}'}
        else:
            # normal response from chat
            return response
    except Exception as e:
        print(f"Error getting chat response: {e}")
        return HTTPResponse(status=500, reason="Error getting chat response")