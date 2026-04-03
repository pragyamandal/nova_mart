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
    return {"status": "ok"}


@app.post("/reset")
def reset(request: ResetRequest):
    try:
        observation: Observation = env.reset(request.task_name)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
