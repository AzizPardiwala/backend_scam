from fastapi import APIRouter
from typing import List
from app.schemas.report_schema import ReportResponse

router = APIRouter()

# Temporary storage (replace with DB later)
reports_db = []

# GET ALL
@router.get("/", response_model=List[ReportResponse])
def get_reports():
    return reports_db

# GET ONE
@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int):
    for r in reports_db:
        if r["id"] == report_id:
            return r
    return {"error": "Not found"}

# DELETE
@router.delete("/{report_id}")
def delete_report(report_id: int):
    global reports_db
    reports_db = [r for r in reports_db if r["id"] != report_id]
    return {"message": "Deleted"}