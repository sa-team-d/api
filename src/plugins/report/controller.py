from datetime import datetime
import io
from turtle import dot
from typing import Optional, List, Union
from fastapi import APIRouter, HTTPException, Depends, Request
from fpdf import FPDF
from sympy import content

from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.plugins.user.schema import User
from src.utils import get_collection

from .schema import Report, ReportResponse
from . import repository as repo
from openai import OpenAI
from src.plugins.kpi import service as kpi_service
import markdown
import pdfkit
import os
from firebase_admin import storage

import dotenv
dotenv.load_dotenv()

API_VERSION = os.getenv("VERSION")
debug_mode = os.getenv("DEBUG")

router = APIRouter(prefix=f"/api/{API_VERSION}/report", tags=["Report"])

prompt = """
You are a Generative AI Assistant for Industry Analysis, acting as a Retrieval-Augmented Generation (RAG) model. Your task is to:

Analyze structured JSON input files containing industrial data and extract key insights.
Generate a detailed, professional-quality report based on the data, including:
- Executive Summary
- Key Performance Indicators (KPIs)
- Trends and Observations
- Recommendations
- Data Appendix
Organize the report with clear sections, headings, and subheadings. Use bullet points, tables.
Format the output to be easily converted into a clean, well-structured PDF.
"""

# create report
@router.post("/", status_code=201, summary="Create a new report, save it to the database and return it")
async def create_report(request: Request, name: str, site: str, kpi_names: Union[List[str],str] , frequency: str, start_date:str, end_date:str, user: User = Depends(verify_firebase_token)):

    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")

    # check if the report name already exists
    #report = await repo.report_by_name(request, name, user.uid)
    #if report:
    #    raise HTTPException(status_code=400, detail="Report name already exists")

    # 1. Get corrispondent kpi data from the kpi service
    # kpi_data = await kpi_service.get_kpi_data(request, kpi_names, start_date, end_date, frequency)

    # 2. Compute the report with the kpi data as input
    try:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "system", "content": f"Consider that you have the following Knowledge Base: {kpi_names}"},
            ]
        )
        report_content = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error getting chat response") from e

    # 3. Convert report content to PDF
    try:
        # Convert Markdown to HTML
        html_content = markdown.markdown(report_content)

        # Configure pdfkit options if needed
        options = {
            'encoding': "UTF-8",
            'enable-local-file-access': None
        }

        # Convert HTML to PDF
        pdf_bytes = pdfkit.from_string(html_content, False, options=options)

        # Create BytesIO object from PDF bytes
        pdf_output = io.BytesIO(pdf_bytes)
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return ReportResponse(success=False, data=None, message="Error creating PDF")

    # 4. Save locally PDF to test (Optional: Remove in production)
    if debug_mode:
        try:
            with open(f'reports/{name}.pdf', "wb") as f:
                f.write(pdf_output.read())
            pdf_output.seek(0)  # Reset buffer after reading
        except Exception as e:
            print(f"Error saving PDF locally: {e}")
            return ReportResponse(success=False, data=None, message="Error saving PDF locally")

    # 5. save pdf on firebase storage
    try:
        bucket = storage.bucket()
        blob = bucket.blob(f"report/{name}.pdf")
        blob.upload_from_file(pdf_output, content_type="application/pdf")
        blob.make_public()
        pdf_url = blob.public_url
    except Exception as e:
        print(f"Error uploading PDF to Firebase Storage: {e}")
        return ReportResponse(success=False, data=None, message="Error uploading PDF to Firebase Storage")

    # 6. Save the report to the database
    # TODO: Save the report to the database: name, site, kpi_names, frequency, start_date, end_date, user_uid, pdf_url

    return pdf_url

# get all reports from all sites
@router.get("/", status_code=200, response_model=ReportResponse, summary="Get all reports created by the user")
async def get_all_reports(request: Request, user: User = Depends(verify_firebase_token)):
    try:
        reports = await repo.reports_by_user_uid(request, user.uid)
        return ReportResponse(success=True, data=reports, message="Reports retrieved successfully")
    except Exception as e:
        return ReportResponse(success=False, data=None, message=str(e))

# filter reports by site
@router.get("/filter", status_code=200, response_model=ReportResponse, summary="Get all reports for a specific machine created by the logged user")
async def get_reports_by_machine_id(request: Request, machine_id: str, user: User = Depends(verify_firebase_token)):
    try:
        if machine_id:
            reports = await repo.reports_by_machine_id(request, machine_id, user.uid)
        else:
            return ReportResponse(success=False, data=None, message="No filter provided")
        return ReportResponse(success=True, data=reports, message="Reports retrieved successfully")
    except Exception as e:
        return ReportResponse(success=False, data=None, message=str(e))