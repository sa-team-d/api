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

#from .service import cost_prediction, utilization_analysis, energy_efficency_analysis
COST_PREDICTION_DATA = {
      "Testing Machines": 0.010329395319865256,
      "Metal Cutting Machines": 0.04637815462858034,
      "Laser Cutter": 0.0005160956082603602,
      "Assembly Machines": 0.007193601533433455,
      "Riveting Machine": 0.009630899430778293,
      "Laser Welding Machines": 0.023551859302206688
}
UTILIZATION_DATA = {
      "Assembly Machine 1": 0.7296168144672052,
      "Laser Cutter": 0.7133254505802838,
      "Assembly Machine 2": 0.6512304181921241,
      "Laser Welding Machine 1": 0.6318166296651799,
      "Low Capacity Cutting Machine 1": 0.5309211020844607,
      "Riveting Machine": 0.5239875385630702,
      "Testing Machine 3": 0.5130672106001118,
      "Testing Machine 2": 0.3916499889917053,
      "Assembly Machine 3": 0.34396030393639204,
      "Laser Welding Machine 2": 0.3254009269969588,
      "Large Capacity Cutting Machine 2": 0.29546711720282665,
      "Large Capacity Cutting Machine 1": 0.21444010156644838,
      "Medium Capacity Cutting Machine 1": 0.20976462895643624,
      "Medium Capacity Cutting Machine 2": 0.07068717738062205,
      "Medium Capacity Cutting Machine 3": 0.058858120003513856,
      "Testing Machine 1": 0.002657429652367055
}
ENERGY_EFFICIENCY_DATA = {
      "Testing Machine 3": 0.0,
      "Testing Machine 2": 0.003305897555474169,
      "Laser Cutter": 0.025994032221087916,
      "Low Capacity Cutting Machine 1": 0.02831853305591658,
      "Assembly Machine 2": 0.07108557042553068,
      "Assembly Machine 3": 0.08959678406509398,
      "Laser Welding Machine 1": 0.13044239797815696,
      "Medium Capacity Cutting Machine 3": 0.17869265637561005,
      "Testing Machine 1": 0.18376660997739142,
      "Assembly Machine 1": 0.18989313186292664,
      "Laser Welding Machine 2": 0.20274847160138532,
      "Large Capacity Cutting Machine 1": 0.22245912392915823,
      "Riveting Machine": 0.3245563678129189,
      "Medium Capacity Cutting Machine 2": 0.3723443960181457,
      "Large Capacity Cutting Machine 2": 0.382136653658655,
      "Medium Capacity Cutting Machine 1": 0.3917457036691058
}

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
chat_memory: Dict[str, Dict[str, any]] = {}

def analyze_query(query: str) -> str:
    """Analyze the query to determine if it's for chat or KPI generation."""
    kpi_keywords = ["create", "generate", "design", "new kpi", "new kpis", "crea", "creare", "genera", "generare", "nuovo kpi", "nuovi kpi"]
    if any(keyword in query.lower() for keyword in kpi_keywords):
        return KPI_PROMPT
    return CHAT_PROMPT

async def fetch_analysis(query: str):
    """Fetch only the necessary analysis data based on the query."""
    cost_terms = {"cost prediction", "previsione dei costi"}
    utilization_terms = {"utilization", "utilisation", "usage", "utilizzo"}
    energy_efficiency_terms = {"energy efficiency", "efficienza energetica"}

    query_lower = query.lower()  # Convert once for efficiency

    cost_data = None
    utilization_data = None
    energy_efficiency_data = None

    if any(term in query_lower for term in cost_terms):
        logger.info("Fetching cost prediction data...")
        cost_data = COST_PREDICTION_DATA
    
    if any(term in query_lower for term in utilization_terms):
        logger.info("Fetching utilization data...")
        utilization_data = UTILIZATION_DATA
    
    if any(term in query_lower for term in energy_efficiency_terms):
        logger.info("Fetching energy efficiency data...")
        energy_efficiency_data = ENERGY_EFFICIENCY_DATA

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
        chat_memory[session_id] = {"past_interactions": []}

    # Get the prompt based on the query intent (chat / KPI generation)
    prompt = analyze_query(query)

    # Fetch knowledge base
    all_kpi: List[KPIOverview] = await kpi_service.listKPIs(site=site_id, request=request)
    all_machines = await machine_repository.get_all(request)
    all_machines = [(machine.name, machine.category) for machine in all_machines]

    # Check if the data is already in session memory and use it if present
    cost_prediction_for_category = chat_memory[session_id].get("cost_prediction_for_category", None)
    utilization = chat_memory[session_id].get("utilization", None)
    energy_efficiency = chat_memory[session_id].get("energy_efficiency", None)

    if not cost_prediction_for_category or not utilization or not energy_efficiency:
        # Fetch analysis data dynamically if not in memory
        cost_prediction_for_category, utilization, energy_efficiency = await fetch_analysis(query)

        # Store the fetched data in the session memory to avoid refetching in future queries
        chat_memory[session_id]["cost_prediction_for_category"] = cost_prediction_for_category
        chat_memory[session_id]["utilization"] = utilization
        chat_memory[session_id]["energy_efficiency"] = energy_efficiency

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

    messages += chat_memory[session_id]["past_interactions"] + [{"role": "user", "content": query}]

    try:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        response = completion.choices[0].message.content

        # Update chat memory
        chat_memory[session_id]["past_interactions"].append({"role": "user", "content": query})
        chat_memory[session_id]["past_interactions"].append({"role": "assistant", "content": response})

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