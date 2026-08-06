from fastapi import FastAPI
from pydantic import BaseModel
from core.agent import OmniAssist

app = FastAPI(title="OmniAssist API", version="2026.3")
agent = OmniAssist()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/run")
def run_agent_endpoint(req: PromptRequest):
    response = agent.run(req.prompt)
    return {"response": response}
