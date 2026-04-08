from environment.models import Observation, Action, Reward
from environment.tasks import TASKS, grade_episode
from environment.data import CUSTOMERS, ORDERS
from environment.tools import (lookup_order, check_policy, verify_defect,
    check_loyalty, process_refund, issue_store_credit, process_exchange,
    escalate_to_manager)

AVAILABLE_ACTIONS = ["lookup_order", "check_policy", "verify_defect", 
    "check_loyalty", "process_refund", "issue_store_credit", 
    "process_exchange", "escalate_to_manager", "respond_to_customer"]

class NovaMartEnv:

    def __init__(self):
        self.current_task = None
        self.action_history = []
        self.conversation_history = []
        self.step_count = 0
        self.max_steps = 10
        self.cumulative_reward = 0.0
        self.done = False
        self.last_tool_result = {}

    def reset(self, task_name: str) -> Observation:
        task = TASKS[task_name]
        self.current_task = task
        self.action_history = []
        self.conversation_history = [task["customer_message"]]
        self.step_count = 0
        self.cumulative_reward = 0.0
        self.done = False
        self.last_tool_result = {}
        customer = CUSTOMERS[task["customer_id"]]
        order = ORDERS[task["order_id"]]
        return Observation(
            customer_id=task["customer_id"],
            customer_name=customer["name"],
            issue_description=task["customer_message"],
            order_id=task["order_id"],
            days_since_purchase=order["days_ago"],
            customer_tier=customer["tier"],
            conversation_history=self.conversation_history.copy(),
            available_actions=AVAILABLE_ACTIONS,
            step_number=self.step_count,
            max_steps=self.max_steps,
            tools_used=[],
            last_tool_result={}
        )

    def step(self, action: Action) -> tuple[Observation, Reward, bool, dict]:
        if self.done:
            raise RuntimeError("Episode is done. Call reset() first.")
        
        self.step_count += 1
        self.action_history.append(action.action_type)
        
        if action.message:
            self.conversation_history.append(f"Agent: {action.message}")
        
        self.last_tool_result = self._execute_action(action)
        
        self.done = (
            self.step_count >= self.max_steps or
            action.action_type == "respond_to_customer"
        )
        
        step_reward = self._calculate_reward(action)
        self.cumulative_reward += step_reward
        
        reward = Reward(
            step_reward=step_reward,
            cumulative_reward=self.cumulative_reward,
            resolution_score=grade_episode(self.current_task["name"], 
                self.action_history) if self.done else 0.0,
            tool_use_score=0.25 if action.action_type != "respond_to_customer" else 0.0,
            communication_score=0.25 if action.message else 0.0,
            penalty=0.0,
            feedback=self._get_feedback(action)
        )
        
        obs = Observation(
            customer_id=self.current_task["customer_id"],
            customer_name=CUSTOMERS[self.current_task["customer_id"]]["name"],
            issue_description=self.current_task["customer_message"],
            order_id=self.current_task["order_id"],
            days_since_purchase=ORDERS[self.current_task["order_id"]]["days_ago"],
            customer_tier=CUSTOMERS[self.current_task["customer_id"]]["tier"],
            conversation_history=self.conversation_history.copy(),
            available_actions=AVAILABLE_ACTIONS,
            step_number=self.step_count,
            max_steps=self.max_steps,
            tools_used=self.action_history.copy(),
            last_tool_result=self.last_tool_result
        )
        
        return obs, reward, self.done, {}

    def state(self) -> dict:
        return {
            "task": self.current_task["name"] if self.current_task else None,
            "step": self.step_count,
            "max_steps": self.max_steps,
            "done": self.done,
            "action_history": self.action_history.copy(),
            "conversation_history": self.conversation_history.copy(),
            "cumulative_reward": self.cumulative_reward,
            "last_tool_result": self.last_tool_result
        }

    def _execute_action(self, action: Action) -> dict:
        t = action.action_type
        inp = action.action_input
        order_id = self.current_task["order_id"]
        customer_id = self.current_task["customer_id"]
        order = ORDERS[order_id]

        if t == "lookup_order":
            return lookup_order(inp.get("order_id", order_id))
        elif t == "check_policy":
            return check_policy(
                inp.get("policy_type", "standard_return"),
                inp.get("days_since_purchase", order["days_ago"])
            )
        elif t == "verify_defect":
            return verify_defect(
                inp.get("order_id", order_id),
                inp.get("defect_description", "")
            )
        elif t == "check_loyalty":
            return check_loyalty(inp.get("customer_id", customer_id))
        elif t == "process_refund":
            return process_refund(
                inp.get("order_id", order_id),
                inp.get("amount", order["amount"])
            )
        elif t == "issue_store_credit":
            amount = inp.get("amount", order["amount"] * 0.3)
            return issue_store_credit(
                inp.get("customer_id", customer_id),
                amount,
                inp.get("reason", "goodwill")
            )
        elif t == "process_exchange":
            return process_exchange(
                inp.get("order_id", order_id),
                inp.get("new_product_id", "PROD-101")
            )
        elif t == "escalate_to_manager":
            return escalate_to_manager(
                inp.get("order_id", order_id),
                inp.get("reason", "customer request")
            )
        elif t == "respond_to_customer":
            return {"message_sent": True, "message": action.message}
        else:
            return {"error": f"Unknown action type: {t}"}

    def _calculate_reward(self, action: Action) -> float:
        task_name = self.current_task["name"]
        action_type = action.action_type
        
        if self.action_history.count(action_type) > 1:
            return 0.0
        
        good_actions = {
            "easy_refund": ["lookup_order", "check_policy", "process_refund"],
            "defect_resolution": ["lookup_order", "verify_defect", "check_policy", "process_refund"],
            "loyalty_constraint": ["lookup_order", "check_loyalty", "verify_defect", "issue_store_credit"]
        }
        
        if action_type in good_actions.get(task_name, []):
            return 0.15
        
        if action_type == "respond_to_customer":
            final_score = grade_episode(task_name, self.action_history)
            # Scale by number of correct steps taken
            step_bonus = min(len(self.action_history) * 0.05, 0.3)
            return max(0.0, (final_score * 0.4) + step_bonus)
        
        return 0.05

    def _get_feedback(self, action: Action) -> str:
        if self.done:
            score = grade_episode(self.current_task["name"], self.action_history)
            return f"Episode complete. Final resolution score: {score:.3f}"
        return f"Action '{action.action_type}' executed successfully."
