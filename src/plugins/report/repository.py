from typing import Optional
from bson import ObjectId
from pymongo.collection import Collection
from fastapi import Request

from src.plugins.report.schema import Report, ReportOverview, ReportDetail
from src.utils import get_collection, create_report_collection
from src.custom_exceptions import ReportNotFoundException



# To create the report collection:
# report_collection = await create_report_collection(request)



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
                "foreignField": "_id",
                "as": "site"
            }
        },
        {
            "$project": {
                "site": 1,
                "content": 1,
                "date": 1,
                "kpi_name": 1,
                "user_uid": 1
            }
        }
    ]

    if report_id:
        pipeline.insert(1, {"$match": {"_id": ObjectId(report_id)}})

    cursor = report_collection.aggregate(pipeline)
    reports_overview = [ReportOverview(**report) async for report in cursor]

    return reports_overview


async def all_reports(request: Request | None = None, report_collection: Collection[Report] | None = None):
    report_collection = get_collection(request=request, name="reports")



    cursor = report_collection.find({})
    all_reports = [ReportDetail(**report) async for report in cursor]

    if all_reports is None or len(all_reports) == 0:
        raise ReportNotFoundException("No reports found")
    return all_reports



async def reports_by_site_id(request: Request, site_id: str, user_uid: Optional[str] = None, report_collection: Collection[Report] | None = None):
    report_collection = get_collection(request=request, name="reports")

    if user_uid:
        cursor = report_collection.find({"sites_id": {"$in": [site_id]}, "user_uid": user_uid})
    else:
        cursor = cursor = report_collection.find({"sites_id": {"$in": [site_id]}})
    reports = [ReportDetail(**report) async for report in cursor]

    if reports is None or len(reports) == 0:
        raise ReportNotFoundException(f"No reports found for machine_id {site_id}")
    return reports

async def reports_by_user_uid(request: Request, user_uid: str, report_collection: Collection[Report] | None = None):
    report_collection = get_collection(request=request, name="reports")

    reports = await get_reports_with_site(user_uid, report_collection)

    if reports is None or len(reports) == 0:
        raise ReportNotFoundException(f"No reports found for user_uid {user_uid}")
    return reports

async def report_by_name(request: Request, name: str, report_collection: Collection[Report] | None = None):
    report_collection = get_collection(request=request, name="reports")

    cursor = report_collection.find({"name": name})
    report = await cursor.to_list(1)

    if report is None or len(report) == 0:
        raise ReportNotFoundException(f"No reports found for name {name}")
    return ReportDetail(**report[0])


async def create_report(request: Request, report: Report, report_collection: Collection[Report] | None = None):
    report_collection = get_collection(request=request, name="reports")

    result = await report_collection.insert_one(report.model_dump())

    return result.inserted_id