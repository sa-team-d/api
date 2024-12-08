from datetime import datetime
import io
from turtle import dot
from typing import Annotated, Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fpdf import FPDF
from sympy import Union, content

from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.plugins.user.schema import User

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
@router.post("/", status_code=201, summary="Create a new report, save it to the database and return the PDF URL to download it")
async def create_report(request: Request, name: str, site: int, kpi_names:  Annotated[list[str] | None, Query()] = None, start_date:str = "2024-09-30 00:00:00", end_date:str = "2024-10-14 00:00:00", operation: str='avg', user: User = Depends(verify_firebase_token)):

    """
    Create a new report, save it to the database and return the PDF URL to download it

    Args:
    - name: the name of the report
    - site: the site for which the report is created
    - kpi_names: the names of the KPIs to include in the report
    - start_date: the start date for the report
    - end_date: the end date for the report
    - user: the user creating the report
    - operation: the operation to perform on the KPIs (sum, avg, min, max)

    Returns:
    - PDF URL to download the report
    """
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return ReportResponse(success=False, data=None, message="Invalid date format. Please use the format 'YYYY-MM-DD HH:MM:SS'")

    if start_date_obj > end_date_obj:
        return ReportResponse(success=False, data=None, message="Start date must be before end date")

    if not kpi_names:
        return ReportResponse(success=False, data=None, message="KPI names must be provided")

    if not site:
        return ReportResponse(success=False, data=None, message="Site must be provided")

    if not name:
        return ReportResponse(success=False, data=None, message="Report name must be provided")

    if not operation:
        return ReportResponse(success=False, data=None, message="Operation must be provided")

    try:
        # check if the report name already exists
        report = await repo.report_by_name(request, name, user.uid)
        if report:
            return ReportResponse(success=False, data=None, message="Report name already exists")
    except Exception as e:
        pass

    # 1. Get corrispondent kpi data from the kpi service
    kb = None

    # 2. Compute the report with the kpi data as input
    try:
        kb = await kpi_service.computeKPIForReport(request, site, start_date_obj, end_date_obj, None, operation)
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "system", "content": f"Consider that you have the following Knowledge Base: {kb}"},
            ]
        )
        report_content = completion.choices[0].message.content
    except Exception as e:
        return ReportResponse(success=False, data=None, message=f"Error generating report: {e}")

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
            return ReportResponse(success=False, data=None, message="Error saving PDF locally")
    # 5. save pdf on firebase storage
    try:
        bucket = storage.bucket()
        blob = bucket.blob(f"report/{name}.pdf")
        blob.upload_from_file(pdf_output, content_type="application/pdf")
        blob.make_public()
        pdf_url = blob.public_url
    except Exception as e:
        return ReportResponse(success=False, data=None, message="Error saving PDF to Firebase Storage")

    # 6. Save the report to the database
    try:

        report = await repo.create_report(request, name, site, kpi_names, start_date_obj, end_date_obj, user.uid, pdf_url)
        return ReportResponse(success=True, data=report, message="Report created successfully")
    except Exception as e:
        return ReportResponse(success=False, data=None, message=str(e))

# get all reports from all sites
@router.get("/", status_code=200, response_model=ReportResponse, summary="Get all reports created by the user")
async def get_all_reports(request: Request, user: User = Depends(verify_firebase_token)):
    """
    Get all reports created by the user

    Args:
    - user: the user creating the report

    Returns:
    - List of reports created by the user
    """
    try:
        reports = await repo.reports_by_user_uid(request, user.uid)
        return ReportResponse(success=True, data=reports, message="Reports retrieved successfully")
    except Exception as e:
        return ReportResponse(success=False, data=None, message=str(e))

# filter reports by site
@router.get("/filter", status_code=200, response_model=ReportResponse, summary="Get all reports for a specific site created by the logged user")
async def get_reports_by_site_id(request: Request, site_id: int = None, name:str = None, user: User = Depends(verify_firebase_token)):
    """
    Get all reports for a specific site created by the logged user

    Args:
    - site_id: the site ID to filter the reports
    - name: the name of the report to filter

    Returns:
    - List of reports for the site
    """
    try:
        print(f"Site ID: {site_id} -- Name: {name}")
        if site_id is not None:
            reports = await repo.reports_by_site_id(request, site_id, name, user.uid)
        elif name:
            reports = await repo.report_by_name(request, name)
        else:
            return ReportResponse(success=False, data=None, message="No filter provided")
        return ReportResponse(success=True, data=reports, message="Reports retrieved successfully")
    except Exception as e:
        return ReportResponse(success=False, data=None, message=str(e))

# delete report
@router.delete("/{report_id}", status_code=200, response_model=ReportResponse, summary="Delete a report by ID")
async def delete_report(request: Request, report_id: str, user: User = Depends(verify_firebase_token)):
    """
    Delete a report by ID

    Args:
    - report_id: the ID of the report to delete
    - user: the user deleting the report

    Returns:
    - Success message if the report is deleted
    """
    try:
        result = await repo.delete_report(request, report_id, user.uid)
        return ReportResponse(success=True, data=result, message="Report deleted successfully")
    except Exception as e:
        return ReportResponse(success=False, data=None, message=str(e))
