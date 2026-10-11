from datetime import date
from typing import Annotated, Literal, Optional

import mysql.connector
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StringConstraints

from db import get_connection

app = FastAPI(title="Research Opportunity Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Validation models ----------

Text = lambda max_len: Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=max_len)
]


class OpportunityCreate(BaseModel):
    title: Text(200)
    description: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    research_area: Text(100)
    faculty_name: Text(100)
    department: Text(100)
    required_skills: Text(255)
    available_positions: int
    application_deadline: date
    status: Literal["Open", "Closed"] = "Open"


class OpportunityUpdate(BaseModel):
    # every field optional, so PUT can change just one thing (e.g. status)
    title: Optional[Text(200)] = None
    description: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]] = None
    research_area: Optional[Text(100)] = None
    faculty_name: Optional[Text(100)] = None
    department: Optional[Text(100)] = None
    required_skills: Optional[Text(255)] = None
    available_positions: Optional[int] = None
    application_deadline: Optional[date] = None
    status: Optional[Literal["Open", "Closed"]] = None


def check_positions(value):
    if value is not None and value < 0:
        raise HTTPException(status_code=400, detail="available_positions cannot be negative")


# ---------- Error handlers ----------

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = [f"{e['loc'][-1]}: {e['msg']}" for e in exc.errors()]
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid or missing data", "errors": errors},
    )


@app.exception_handler(mysql.connector.Error)
async def db_error_handler(request: Request, exc: mysql.connector.Error):
    return JSONResponse(status_code=500, content={"detail": "Database error"})


@app.exception_handler(Exception)
async def generic_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ---------- Helpers ----------

def fetch_one(opportunity_id: int):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM opportunities WHERE id = %s", (opportunity_id,))
        return cur.fetchone()
    finally:
        conn.close()


# ---------- Endpoints ----------

@app.get("/api/health")
def health():
    conn = get_connection()
    conn.close()
    return {"status": "ok", "database": "connected"}


@app.post("/api/opportunities", status_code=201)
def create_opportunity(data: OpportunityCreate):
    check_positions(data.available_positions)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO opportunities
               (title, description, research_area, faculty_name, department,
                required_skills, available_positions, application_deadline, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                data.title, data.description, data.research_area, data.faculty_name,
                data.department, data.required_skills, data.available_positions,
                data.application_deadline, data.status,
            ),
        )
        conn.commit()
        new_id = cur.lastrowid
    finally:
        conn.close()
    return fetch_one(new_id)


@app.get("/api/opportunities")
def get_all_opportunities():
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM opportunities ORDER BY id DESC")
        return cur.fetchall()
    finally:
        conn.close()


@app.get("/api/opportunities/{opportunity_id}")
def get_opportunity(opportunity_id: int):
    row = fetch_one(opportunity_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return row


@app.put("/api/opportunities/{opportunity_id}")
def update_opportunity(opportunity_id: int, data: OpportunityUpdate):
    if fetch_one(opportunity_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    check_positions(changes.get("available_positions"))

    set_clause = ", ".join(f"{col} = %s" for col in changes)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE opportunities SET {set_clause} WHERE id = %s",
            (*changes.values(), opportunity_id),
        )
        conn.commit()
    finally:
        conn.close()
    return fetch_one(opportunity_id)


@app.delete("/api/opportunities/{opportunity_id}")
def delete_opportunity(opportunity_id: int):
    if fetch_one(opportunity_id) is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM opportunities WHERE id = %s", (opportunity_id,))
        conn.commit()
    finally:
        conn.close()
    return {"message": "Opportunity deleted successfully"}