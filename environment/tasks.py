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
    tools_used = [a for a in action_history if a != "respond_to_customer"]

    if task_name == "easy_refund":
        if "process_refund" in action_history:
            if "check_policy" in action_history and action_history.index("check_policy") < action_history.index("process_refund"):
                if "verify_defect" in action_history:
                    return 0.5
                return 0.7
            return 0.4
        if "check_policy" in action_history:
            return 0.3
        if not tools_used:
            return 0.1
        return 0.0

    elif task_name == "defect_resolution":
        if "process_refund" in action_history:
            if "verify_defect" in action_history and action_history.index("verify_defect") < action_history.index("process_refund"):
                return 0.85  # correct defect path
            return 0.0  # refund without verifying defect
        if "issue_store_credit" in action_history:
            return 0.65
        if "escalate_to_manager" in action_history:
            return 0.55
        if not tools_used:
            return 0.1
        if "check_policy" in action_history or "lookup_order" in action_history:
            return 0.3
        return 0.0

    elif task_name == "loyalty_constraint":
        if "process_refund" in action_history:
            return 0.0  # wrong, defect not confirmed
        if "issue_store_credit" in action_history and "check_loyalty" in action_history:
            if action_history.index("check_loyalty") < action_history.index("issue_store_credit"):
                return 1.0  # perfect path
            return 0.7
        if "escalate_to_manager" in action_history:
            return 0.6
        if "check_loyalty" in action_history:
            return 0.4
        if not tools_used:
            return 0.1
        return 0.0

    return 0.0
