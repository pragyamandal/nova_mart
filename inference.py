import os
import json
import asyncio

import httpx
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")

ENV_URL = "http://localhost:7860"

SYSTEM_PROMPT = """You are a customer service agent at NovaMart electronics store.
Resolve customer issues by using the available tools and actions.
Always investigate the order and check policies before taking resolution actions.
Respond with ONLY a valid JSON object with exactly these fields:
{
  'action_type': one of [lookup_order, check_policy, verify_defect, check_loyalty, process_refund, issue_store_credit, process_exchange, escalate_to_manager, respond_to_customer],
  'action_input': dict of parameters for the action,
  'message': string message to customer (can be empty string)
}"""

TASKS = ["easy_refund", "defect_resolution", "loyalty_constraint"]

FALLBACK_ACTION = {
    "action_type": "respond_to_customer",
    "action_input": {},
    "message": "I need to look into this further.",
}


def parse_llm_response(text: str) -> dict:
    """Parse LLM response as JSON, returning fallback action on failure."""
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]  # remove opening ```json or ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        return json.loads(cleaned)
    except (json.JSONDecodeError, Exception):
        return FALLBACK_ACTION.copy()


def fmt_bool(value: bool) -> str:
    """Format boolean as lowercase string."""
    return "true" if value else "false"


async def run_task(task_name: str, client: AsyncOpenAI) -> float:
    """Run a single task and return the score."""
    rewards = []
    steps = 0
    success = False

    print(f"[START] task={task_name} env=novamart-customer-service model={MODEL_NAME}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as http:
            # Reset environment
            reset_resp = await http.post(
                f"{ENV_URL}/reset",
                json={"task_name": task_name},
            )
            reset_resp.raise_for_status()
            observation = reset_resp.json()

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(observation)},
            ]

            done = False
            has_looked_up_order = False
            has_checked_policy = False

            while not done and steps < 10:
                # Get action from LLM
                completion = await client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                )
                llm_text = completion.choices[0].message.content
                action = parse_llm_response(llm_text)

                # --- Enforce action ordering ---
                # 1. Must call lookup_order before anything else
                if not has_looked_up_order and action["action_type"] != "lookup_order":
                    action = {
                        "action_type": "lookup_order",
                        "action_input": action.get("action_input", {}),
                        "message": "",
                    }

                # 2. Must call check_policy before respond_to_customer
                if (
                    has_looked_up_order
                    and not has_checked_policy
                    and action["action_type"] == "respond_to_customer"
                ):
                    action = {
                        "action_type": "check_policy",
                        "action_input": action.get("action_input", {}),
                        "message": "",
                    }

                # Track completed prerequisites
                if action["action_type"] == "lookup_order":
                    has_looked_up_order = True
                if action["action_type"] == "check_policy":
                    has_checked_policy = True

                # Step environment
                step_resp = await http.post(
                    f"{ENV_URL}/step",
                    json=action,
                )
                step_resp.raise_for_status()
                result = step_resp.json()

                observation = result["observation"]
                reward_data = result["reward"]
                done = result["done"]
                step_reward = reward_data["step_reward"]
                rewards.append(step_reward)
                steps += 1

                print(
                    f"[STEP]  step={steps} "
                    f"action={action['action_type']} "
                    f"reward={step_reward:.2f} "
                    f"done={fmt_bool(done)} "
                    f"error=null"
                )

                # Append assistant + new observation to conversation
                messages.append({"role": "assistant", "content": llm_text})
                messages.append(
                    {"role": "user", "content": json.dumps(observation)}
                )

            success = True

    except Exception:
        success = False

    finally:
        score = sum(rewards) / max(len(rewards), 1)
        score = max(0.0, min(1.0, score))
        rewards_str = ",".join(f"{r:.2f}" for r in rewards)
        print(
            f"[END]   success={fmt_bool(success)} "
            f"steps={steps} "
            f"score={score:.3f} "
            f"rewards={rewards_str}"
        )

    return score


async def main():
    """Run all tasks and print final results."""
    client = AsyncOpenAI(
        base_url=API_BASE_URL,
        api_key=HF_TOKEN,
    )

    scores = {}
    for task_name in TASKS:
        score = await run_task(task_name, client)
        scores[task_name] = score

    avg = sum(scores.values()) / len(scores)

    print()
    print("=== FINAL RESULTS ===")
    print(f"easy_refund:        {scores['easy_refund']:.3f}")
    print(f"defect_resolution:  {scores['defect_resolution']:.3f}")
    print(f"loyalty_constraint: {scores['loyalty_constraint']:.3f}")
    print(f"average:            {avg:.3f}")


if __name__ == "__main__":
    asyncio.run(main())
