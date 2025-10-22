from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

@app.get("/")
def root():
    return {"message": "¡Nadakki AI Suite está activo!"}

class Call(BaseModel):
    agent: str
    tenant: str
    vars: dict

class DispatchPayload(BaseModel):
    calls: List[Call]

@app.post("/api/dispatch")
def dispatch(payload: DispatchPayload):
    return {
        "status": "OK",
        "executed": [
            {
                "agent": call.agent,
                "tenant": call.tenant,
                "vars": call.vars
            }
            for call in payload.calls
        ]
    }

