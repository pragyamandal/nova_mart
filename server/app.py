from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from environment.env import NovaMartEnv
from environment.models import Observation, Action, Reward


app = FastAPI(title="NovaMart Customer Service Environment")
env = NovaMartEnv()


class ResetRequest(BaseModel):
    task_name: str = "easy_refund"


@app.get("/")
def root():
    return {"message": "NovaMart Customer Service Environment", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metadata")
def metadata():
    return {
        "name": "novamart-customer-service",
        "description": "A customer service constraint negotiation environment where an AI agent resolves customer complaints at NovaMart within real policy constraints.",
        "version": "1.0.0",
        "tasks": ["easy_refund", "defect_resolution", "loyalty_constraint"]
    }


@app.get("/schema")
def schema():
    return {
        "action": {
            "type": "object",
            "fields": ["action_type", "action_input", "message"]
        },
        "observation": {
            "type": "object", 
            "fields": ["customer_id", "customer_name", "issue_description", 
                      "order_id", "days_since_purchase", "customer_tier",
                      "conversation_history", "available_actions", 
                      "step_number", "max_steps", "tools_used", "last_tool_result"]
        },
        "state": {
            "type": "object",
            "fields": ["current_task", "step_number", "action_history", 
                      "cumulative_reward", "done"]
        }
    }


@app.post("/mcp")
def mcp(request: dict = None):
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "name": "novamart-customer-service",
            "description": "OpenEnv customer service environment"
        }
    }


@app.post("/reset")
def reset(request: ResetRequest = None):
    try:
        task = request.task_name if request else "easy_refund"
        observation: Observation = env.reset(task)
        return observation
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@app.post("/step")
def step(action: Action):
    try:
        observation, reward, done, info = env.step(action)
        return {
            "observation": observation,
            "reward": reward,
            "done": done,
            "info": info,
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@app.get("/state")
def state():
    return env.state()

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
