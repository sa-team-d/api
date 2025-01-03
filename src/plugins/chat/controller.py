import json
import os
import logging

from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, Request

from openai import OpenAI

from src.plugins.auth.firebase import verify_firebase_token
from src.plugins.chat.schema import Analysis, ChatResponse
from src.plugins.kpi import service as kpi_service
from src.plugins.machine import repository as machine_repository
from src.plugins.kpi.schema import KPIOverview

from .service import cost_prediction, utilization_analysis, energy_efficency_analysis

# Prompts
CHAT_PROMPT = """You are a specialized AI assistant designed to simulate a Retrieval-Augmented Generation (RAG) system for an industrial domain. 
Your task is to answer general questions related to the knowledge base. 
If the information is not available in the knowledge base, you should politely decline to answer."""

KPI_PROMPT = """You are a specialized AI assistant designed to generate new Key Performance Indicators (KPIs) for an industrial domain.
Your task is to create new KPIs based on the already existing KPIs.
Respond strictly in the following JSON format, without any introductory or explanatory text:
    
{
  "KPIs": [
    {
      "name": "<KPI Name>",
      "type": "<Type of KPI>",
      "description": "<Brief description of the new KPI>",
      "unit_of_measure": "<Unit of measure of the new KPI>",
      "formula": "<Mathematical formula to calculate the new KPI using existing KPIs>"
    }
  ]
}"""

# Logger
logger = logging.getLogger('uvicorn.error')
API_VERSION = os.getenv("VERSION")
DEBUG = os.getenv("DEBUG")

# Router
router = APIRouter(prefix=f"/api/{API_VERSION}/chat", tags=["Chat"])

# Chat memory
chat_memory: Dict[str, List[Dict[str, str]]] = {}

def analyze_query(query: str) -> str:
    """Analyze the query to determine if it's for chat or KPI generation."""
    kpi_keywords = ["create", "generate", "design", "new kpi", "new kpis", "crea", "creare", "genera", "generare", "nuovo kpi", "nuovi kpi"]
    if any(keyword in query.lower() for keyword in kpi_keywords):
        return KPI_PROMPT
    return CHAT_PROMPT

async def fetch_analysis(query: str):
    """Fetch only the necessary analysis data based on the query."""
    cost_terms = {"cost prediction", "previsione dei costi"}
    utilization_terms = {"utilization", "utilizzo"}
    energy_efficiency_terms = {"energy efficiency of", "efficienza energetica della", "efficienza energetica dell'", "efficienza energetica di", "efficienza energetica delle"}

    query_lower = query.lower()  # Convert once for efficiency

    cost_data = None
    utilization_data = None
    energy_efficiency_data = None

    if any(term in query_lower for term in cost_terms):
        logger.info("Fetching cost prediction data...")
        cost_data, _ = cost_prediction()
    
    if any(term in query_lower for term in utilization_terms):
        logger.info("Fetching utilization data...")
        utilization_data = utilization_analysis()
    
    if any(term in query_lower for term in energy_efficiency_terms):
        logger.info("Fetching energy efficiency data...")
        energy_efficiency_data = energy_efficency_analysis()

    return cost_data, utilization_data, energy_efficiency_data

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
    session_id = user.uid  # Use the user's unique ID to track sessions

    # Initialize memory if not present
    if session_id not in chat_memory:
        chat_memory[session_id] = []

    # Get the prompt based on the query intent (chat / KPI generation)
    prompt = analyze_query(query)

    # Fetch knowledge base
    all_kpi: List[KPIOverview] = await kpi_service.listKPIs(site=site_id, request=request)
    all_machines = await machine_repository.get_all(request)
    all_machines = [(machine.name, machine.category) for machine in all_machines]

    # Fetch analysis data dynamically
    cost_prediction_for_category, utilization, energy_efficiency = await fetch_analysis(query)

    # Dynamically include the fetched kb and the chat history in the prompt
    messages = [
        {"role": "system", "content": prompt}
    ] + [
        {"role": "system", "content": f"The company operates a single site with 16 separate machines, each classified into specific types. In particular, there are: 6 metal cutters, 1 riveter, 1 laser cutter, 3 assemblers, 2 welding machines, and 3 testing machines. The available machines are: {all_machines}, and the KPIs associated with each machine are: {all_kpi}."}
    ]
    
    if cost_prediction_for_category:
        messages.append({"role": "system", "content": f"The average daily cost for the next month for each machine category is: {cost_prediction_for_category}."})
    
    if utilization:
        messages.append({"role": "system", "content": f"The utilization analysis for each machine is: {utilization}."})
    
    if energy_efficiency:
        messages.append({"role": "system", "content": f"The energy efficiency analysis for each machine is: {energy_efficiency}."})

    messages += chat_memory[session_id] + [{"role": "user", "content": query}]

    try:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response = completion.choices[0].message.content

        # Update chat memory
        chat_memory[session_id].append({"role": "user", "content": query})
        chat_memory[session_id].append({"role": "assistant", "content": response})

        if response.startswith("{") and response.endswith("}"):
            # JSON response in case of KPI generation
            json_kpi = json.loads(response)
            print(json_kpi)
            created_kpis = []
            for kpi in json_kpi.get("KPIs", []):
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
            return {f'Successfully created KPIs: {created_kpis}'} if created_kpis else {'Impossible to create KPIs'}
        
        # Use case as a chatbot
        return response

    except Exception as e:
        print(f"Error getting chat response: {e}")
        return ChatResponse(success=False, data=None, message=f"Error getting chat response: {str(e)}")

"""@router.get("/", status_code=200, summary="Get ML analysis results")
async def getAnalysis(
    request: Request,
    user=Depends(verify_firebase_token)
):
    """"""
    This endpoint is used to get the analysis results from the ML analysis.
    Returns:
    - dict: The analysis results
    """"""
    try:
        for k, v in cost_prediction_for_category.items():
            cost_prediction_for_category[k] = str(v)

        return ChatResponse(
            success=True,
            data=Analysis(
                cost_prediction=cost_prediction_for_category,
                utilization=utilization.to_dict(),
                energy_efficiency=energy_efficiency.to_dict()
            ),
            message="Analysis results retrieved successfully")

    except Exception as e:
        print(f"Error getting analysis results: {e}")
        return ChatResponse(success=False, data=None, message=f"Error getting analysis results: {str(e)}")"""

@router.post("/reset", status_code=200, summary="Reset chat memory")
async def resetChatMemory(
    user=Depends(verify_firebase_token)
):
    """
    This endpoint resets the chat memory for the user.
    """
    session_id = user.uid
    chat_memory.pop(session_id, None)
    return ChatResponse(success=True, data=None, message="Chat memory reset successfully.")