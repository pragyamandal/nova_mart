from environment.data import CUSTOMERS, ORDERS, POLICIES

TASKS = {
    "easy_refund": {
        "name": "easy_refund",
        "customer_id": "CUST-001",
        "order_id": "ORD-5001",
        "scenario": "Customer wants a refund. Order is 20 days old, unopened.",
        "customer_message": "I haven't opened my new earbuds at all. They've just been sitting here for 20 days. I'd like a refund please."
    },
    "defect_resolution": {
        "name": "defect_resolution",
        "customer_id": "CUST-003",
        "order_id": "ORD-5002",
        "scenario": "Order 40 days ago, opened, defective phone.",
        "customer_message": "my phone stopped working after 2 weeks"
    },
    "loyalty_constraint": {
        "name": "loyalty_constraint",
        "customer_id": "CUST-006",
        "order_id": "ORD-5003",
        "scenario": "Order 55 days ago, gold tier, not defective.",
        "customer_message": "it overheats sometimes but mostly works, I just don't want it anymore"
    }
}

def grade_episode(task_name: str, action_history: list[str]) -> float:
    """
    Grades an agent's performance in a given task based on the list of actions taken.
    Returns a score strictly determined by the deterministic presence and order of actions.
    """
    # Helper to check if agent responded purely via chat without internal tooling
    tools_used = [action for action in action_history if action != "respond_to_customer"]

    if task_name == "easy_refund":
        if "process_refund" in action_history:
            if "check_policy" in action_history and action_history.index("check_policy") < action_history.index("process_refund"):
                return 1.0
            return 0.5 # Wrong resolution / didn't check policy first
        if "check_policy" in action_history:
            return 0.5
        if not tools_used:
            return 0.2
        return 0.0

    elif task_name == "defect_resolution":
        if "process_refund" in action_history:
            if "verify_defect" in action_history and action_history.index("verify_defect") < action_history.index("process_refund"):
                return 1.0
            return -0.3 # Gave refund without verifying
        if "issue_store_credit" in action_history:
            return 0.75
        if not tools_used:
            return 0.1
        if "check_policy" in action_history or "lookup_order" in action_history:
            return 0.4
        return 0.0

    elif task_name == "loyalty_constraint":
        if "process_refund" in action_history:
            return -0.3 # Refunded but defect wasn't verifiable
        if "issue_store_credit" in action_history:
            return 1.0
        if "escalate_to_manager" in action_history:
            return 0.70
        if not tools_used:
            return 0.1
        return 0.0

    return 0.0
