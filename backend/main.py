from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import get_connection

app = FastAPI(title="Research Opportunity Portal API")

# Allows the frontend (a different origin) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    conn = get_connection()
    conn.close()
    return {"status": "ok", "database": "connected"}