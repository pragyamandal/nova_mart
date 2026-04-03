from datetime import datetime, timedelta

from environment.data import CUSTOMERS, ORDERS, PRODUCTS, POLICIES


def lookup_order(order_id: str) -> dict:
    """Look up an order by its ID and return all order details.

    Retrieves the order from the ORDERS dictionary, renaming the
    'days_ago' field to 'days_since_purchase' in the returned result.
    Returns an error dict if the order is not found.
    """
    if order_id not in ORDERS:
        return {"success": False, "error": f"Order '{order_id}' not found."}

    order = ORDERS[order_id]
    return {
        "success": True,
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "product_name": order["product_name"],
        "amount": order["amount"],
        "days_since_purchase": order["days_ago"],
        "status": order["status"],
        "is_opened": order["is_opened"],
        "is_defective": order["is_defective"],
    }


def check_policy(policy_type: str, days_since_purchase: int) -> dict:
    """Check whether a customer is eligible under a given return policy.

    Looks up the policy by type, compares 'days_since_purchase' against
    the policy's window_days to determine eligibility, and returns all
    policy fields alongside the eligibility flag.
    Returns an error dict if the policy type is not found.
    """
    if policy_type not in POLICIES:
        return {"success": False, "error": f"Policy type '{policy_type}' not found."}

    policy = POLICIES[policy_type]
    window = policy["window_days"]
    is_eligible = (window is not None) and (days_since_purchase <= window)

    return {
        "success": True,
        "policy_type": policy_type,
        "is_eligible": is_eligible,
        **policy,
    }


def verify_defect(order_id: str, defect_description: str) -> dict:
    """Verify whether an order's product has a confirmed defect.

    Checks the order's 'is_defective' flag and determines warranty
    eligibility (defective AND purchased within the last 90 days).
    Returns an error dict if the order is not found.
    """
    if order_id not in ORDERS:
        return {"success": False, "error": f"Order '{order_id}' not found."}

    order = ORDERS[order_id]
    is_defective = order["is_defective"]

    return {
        "success": True,
        "is_defective": is_defective,
        "defect_confirmed": is_defective,
        "warranty_eligible": is_defective and order["days_ago"] <= 90,
    }


def check_loyalty(customer_id: str) -> dict:
    """Check a customer's loyalty tier and goodwill-credit eligibility.

    Returns the customer's tier, loyalty points, whether they qualify
    for a goodwill gesture (silver or gold), and their credit percentage.
    Returns an error dict if the customer is not found.
    """
    if customer_id not in CUSTOMERS:
        return {"success": False, "error": f"Customer '{customer_id}' not found."}

    customer = CUSTOMERS[customer_id]
    tier = customer["tier"]

    if tier == "gold":
        credit_percentage = 30
    elif tier == "silver":
        credit_percentage = 20
    else:
        credit_percentage = 0

    return {
        "success": True,
        "tier": tier,
        "loyalty_points": customer["loyalty_points"],
        "is_eligible_for_goodwill": tier in ("silver", "gold"),
        "credit_percentage": credit_percentage,
    }


def process_refund(order_id: str, amount: float) -> dict:
    """Simulate processing a refund for a given order.

    Generates a deterministic transaction ID from the order ID and
    returns the refunded amount. Returns an error dict if the order
    is not found.
    """
    if order_id not in ORDERS:
        return {"success": False, "error": f"Order '{order_id}' not found."}

    return {
        "success": True,
        "transaction_id": "TXN-" + order_id,
        "amount_refunded": amount,
        "error": None,
    }


def issue_store_credit(customer_id: str, amount: float, reason: str) -> dict:
    """Simulate issuing store credit to a customer.

    Generates a deterministic credit code from the customer ID and
    calculates an expiry date 180 days from today. Returns an error
    dict if the customer is not found.
    """
    if customer_id not in CUSTOMERS:
        return {"success": False, "error": f"Customer '{customer_id}' not found."}

    expiry_date = (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")

    return {
        "success": True,
        "credit_code": "CREDIT-" + customer_id,
        "amount": amount,
        "expiry_date": expiry_date,
        "error": None,
    }


def process_exchange(order_id: str, new_product_id: str) -> dict:
    """Simulate processing a product exchange for a given order.

    Looks up both the original order and the new product, then
    generates a deterministic new order ID. Returns an error dict
    if either the order or the product is not found.
    """
    if order_id not in ORDERS:
        return {"success": False, "error": f"Order '{order_id}' not found."}
    if new_product_id not in PRODUCTS:
        return {"success": False, "error": f"Product '{new_product_id}' not found."}

    return {
        "success": True,
        "new_order_id": "ORD-EXCH-" + order_id,
        "exchange_confirmed": True,
        "error": None,
    }


def escalate_to_manager(order_id: str, reason: str) -> dict:
    """Simulate escalating an order issue to a manager for review.

    Generates a deterministic escalation ticket ID from the order ID
    and returns the estimated response time and pending action status.
    """
    return {
        "success": True,
        "ticket_id": "ESC-" + order_id,
        "estimated_response_hours": 24,
        "approved_action": "pending_review",
    }
