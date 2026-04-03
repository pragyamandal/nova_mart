from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field

class Observation(BaseModel):
    """
    Represents the state of the NovaMart customer service environment at a given step.
    This model provides the agent with all necessary context about the customer,
    the current issue, and the available actions to take.
    """
    customer_id: str
    customer_name: str
    issue_description: str
    order_id: str
    days_since_purchase: int
    customer_tier: Literal["standard", "silver", "gold"]
    conversation_history: List[str]
    available_actions: List[str]
    step_number: int
    max_steps: int
    tools_used: List[str]
    last_tool_result: Dict[str, Any]

class Action(BaseModel):
    """
    Represents an action taken by the agent in the NovaMart environment.
    The agent must specify the type of action to perform, the required input data
    for that action, and optionally a message to send to the customer.
    """
    action_type: Literal[
        "lookup_order",
        "check_policy",
        "verify_defect",
        "check_loyalty",
        "process_refund",
        "issue_store_credit",
        "process_exchange",
        "escalate_to_manager",
        "respond_to_customer"
    ]
    action_input: Dict[str, Any]
    message: str = ""

class Reward(BaseModel):
    """
    Represents the feedback and reward signals provided to the agent after taking an action.
    This includes detailed scoring components to help the agent learn optimal behaviors
    in customer resolution and tool usage.
    """
    step_reward: float
    cumulative_reward: float
    resolution_score: float
    tool_use_score: float
    communication_score: float
    penalty: float
    feedback: str
