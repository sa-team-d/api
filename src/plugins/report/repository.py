from datetime import datetime
from typing import Optional
from bson import ObjectId
from pymongo.collection import Collection
from fastapi import Request

from src.plugins.report.schema import Report, ReportOverview, ReportDetail
from src.custom_exceptions import ReportNotFoundException
from src.utils import get_collection



async def get_reports_with_site(user_uid, report_collection: Collection[Report], report_id: Optional[str] = None):

    pipeline = [
        {
            "$match":
            {
                "user_uid": user_uid
            }
        },
        {
        "$unwind": "$sites_id"  # First unwind the asset_id array
        },
        {
            "$lookup": {
                "from": "sites",
                "localField": "sites_id",
                "foreignField": "site_id",
                "as": "site"
            }
        },
        {
            "$project": {
                "site": 1,
                "name": 1,
                "start_date": 1,
                "kpi_names": 1,
                "user_uid": 1,
                "end_date": 1,
                "url": 1
                
            }
        }
    ]

    if report_id:
        pipeline.insert(1, {"$match": {"_id": ObjectId(report_id)}})

    cursor = report_collection.aggregate(pipeline)
    reports_overview = [ReportOverview(**report) async for report in cursor]

    return reports_overview


async def all_reports(request: Request | None = None):
    report_collection = get_collection(request=request, name="reports")



    cursor = report_collection.find({})
    all_reports = [ReportDetail(**report) async for report in cursor]

    if all_reports is None or len(all_reports) == 0:
        raise ReportNotFoundException("No reports found")
    return all_reports



async def reports_by_site_id(request: Request, site_id: int, report_name:str =None,  user_uid: Optional[str] = None):
    report_collection = get_collection(request=request, name="reports")

    if user_uid and report_name:
        cursor = report_collection.find({"sites_id": site_id, "user_uid": user_uid, "name": report_name})
    elif user_uid:
        cursor = cursor = report_collection.find({"sites_id": site_id, "user_uid": user_uid})
    reports = [ReportDetail(**report) async for report in cursor]

    if reports is None or len(reports) == 0:
        raise ReportNotFoundException(f"No reports found for site_id {site_id}")
    return reports

async def reports_by_user_uid(request: Request, user_uid: str):
    report_collection = get_collection(request=request, name="reports")

    reports = await get_reports_with_site(user_uid, report_collection)

    if reports is None or len(reports) == 0:
        raise ReportNotFoundException(f"No reports found for user_uid {user_uid}")
    return reports

async def report_by_name(request: Request, name: str, user_uid: Optional[str] = None):
    report_collection = get_collection(request=request, name="reports")

    if user_uid:
        cursor = report_collection.find({"name": name, "user_uid": user_uid})
    else:
        cursor = report_collection.find({"name": name})
        
    report = await cursor.to_list(1)

    if report is None or len(report) == 0:
        raise ReportNotFoundException(f"No reports found for name {name}")
    return ReportDetail(**report[0])


async def create_report(request: Request, name: str, site: int, kpi_names: list[str], start_date_obj: datetime, end_date_obj: datetime, user_uid: str, pdf_url: str) -> ReportDetail:
   
    
    try:
    
        report_collection = get_collection(request=request, name="reports")
        report_obj = Report(name=name, sites_id=[site], kpi_names=kpi_names, start_date=start_date_obj, end_date=end_date_obj, user_uid=user_uid, url=pdf_url)

        result = await report_collection.insert_one(report_obj.model_dump())

        # Get the inserted document
        created_report = await report_collection.find_one({"_id": result.inserted_id})
        print(f"Created report: {created_report}")
        # Convert to ReportDetail
        return ReportDetail(
            _id=str(created_report["_id"]),
            name=created_report["name"],
            sites_id=created_report["sites_id"],
            kpi_names=created_report["kpi_names"],
            start_date=created_report["start_date"],
            end_date=created_report["end_date"], 
            user_uid=created_report["user_uid"],
            url=created_report["url"]
        )
    except Exception as e:
        raise e