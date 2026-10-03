from fastapi import FastAPI
from pydantic import BaseModel

from incident.investigate import investigate

app = FastAPI(title="Incident investigation")


class Snapshot(BaseModel):
    service: str
    oom_killed: bool = False
    memory_percent: float = 0
    restart_count: int = 0


@app.post("/investigations")
def create(body: Snapshot):
    found = investigate(body.model_dump())
    found["service"] = body.service
    return found
