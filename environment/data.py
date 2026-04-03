CUSTOMERS = {
    "CUST-001": {
        "customer_id": "CUST-001",
        "name": "Alice Johnson",
        "email": "alice.j@example.com",
        "tier": "standard",
        "loyalty_points": 120
    },
    "CUST-002": {
        "customer_id": "CUST-002",
        "name": "Bob Smith",
        "email": "bob.smith@example.com",
        "tier": "standard",
        "loyalty_points": 45
    },
    "CUST-003": {
        "customer_id": "CUST-003",
        "name": "Charlie Davis",
        "email": "charlie.d@example.com",
        "tier": "silver",
        "loyalty_points": 450
    },
    "CUST-004": {
        "customer_id": "CUST-004",
        "name": "Diana Prince",
        "email": "diana.p@example.com",
        "tier": "silver",
        "loyalty_points": 600
    },
    "CUST-005": {
        "customer_id": "CUST-005",
        "name": "Evan Wright",
        "email": "evan.w@example.com",
        "tier": "gold",
        "loyalty_points": 1250
    },
    "CUST-006": {
        "customer_id": "CUST-006",
        "name": "Fiona Gallagher",
        "email": "fiona.g@example.com",
        "tier": "gold",
        "loyalty_points": 3200
    }
}

PRODUCTS = {
    "PROD-101": {
        "product_id": "PROD-101",
        "name": "NovaPhone X",
        "category": "Smartphones",
        "price": 899.99
    },
    "PROD-102": {
        "product_id": "PROD-102",
        "name": "NovaBook Pro",
        "category": "Laptops",
        "price": 1299.99
    },
    "PROD-103": {
        "product_id": "PROD-103",
        "name": "NovaBuds Noise-Cancelling",
        "category": "Audio",
        "price": 149.99
    },
    "PROD-104": {
        "product_id": "PROD-104",
        "name": "NovaWatch S2",
        "category": "Wearables",
        "price": 249.99
    }
}

ORDERS = {
    # Task 1 - easy refund: One order 20 days ago, unopened, not defective
    "ORD-5001": {
        "order_id": "ORD-5001",
        "customer_id": "CUST-001",
        "product_name": "NovaBuds Noise-Cancelling",
        "amount": 149.99,
        "days_ago": 20,
        "status": "delivered",
        "is_opened": False,
        "is_defective": False
    },
    # Task 2 - defect path: One order 40 days ago, opened, is_defective True
    "ORD-5002": {
        "order_id": "ORD-5002",
        "customer_id": "CUST-003",
        "product_name": "NovaPhone X",
        "amount": 899.99,
        "days_ago": 40,
        "status": "delivered",
        "is_opened": True,
        "is_defective": True
    },
    # Task 3 - loyalty credit: One order 55 days ago, opened, not defective
    "ORD-5003": {
        "order_id": "ORD-5003",
        "customer_id": "CUST-006",
        "product_name": "NovaBook Pro",
        "amount": 1299.99,
        "days_ago": 55,
        "status": "delivered",
        "is_opened": True,
        "is_defective": False
    },
    # Three other realistic orders with varied data
    "ORD-5004": {
        "order_id": "ORD-5004",
        "customer_id": "CUST-002",
        "product_name": "NovaWatch S2",
        "amount": 249.99,
        "days_ago": 115, # Past all windows
        "status": "delivered",
        "is_opened": True,
        "is_defective": False
    },
    "ORD-5005": {
        "order_id": "ORD-5005",
        "customer_id": "CUST-004",
        "product_name": "NovaPhone X",
        "amount": 899.99,
        "days_ago": 10,
        "status": "shipped", # Still shipping, perhaps customer checking status
        "is_opened": False,
        "is_defective": False
    },
    "ORD-5006": {
        "order_id": "ORD-5006",
        "customer_id": "CUST-005",
        "product_name": "NovaBuds Noise-Cancelling",
        "amount": 149.99,
        "days_ago": 85,
        "status": "delivered",
        "is_opened": True,
        "is_defective": True # Almost 90 days defective scenario
    }
}

POLICIES = {
    "standard_return": {
        "description": "30 days window, full refund, item must be unopened or unused",
        "window_days": 30,
        "refund_type": "full_refund",
        "condition": "unopened"
    },
    "defective": {
        "description": "90 days window, full refund, defect must be verified",
        "window_days": 90,
        "refund_type": "full_refund",
        "condition": "defect_verified"
    },
    "exchange": {
        "description": "45 days window, item must be unopened, exchange only",
        "window_days": 45,
        "action_type": "exchange",
        "condition": "unopened"
    },
    "loyalty_gold": {
        "description": "60 days window, 30% store credit, gold tier only",
        "window_days": 60,
        "refund_type": "store_credit",
        "credit_percentage": 30,
        "tier_requirement": "gold"
    },
    "loyalty_silver": {
        "description": "60 days window, 20% store credit, silver tier only",
        "window_days": 60,
        "refund_type": "store_credit",
        "credit_percentage": 20,
        "tier_requirement": "silver"
    },
    "manager_exception": {
        "description": "90 days window, case by case, up to full refund",
        "window_days": 90,
        "resolution": "case_by_case"
    },
    "no_resolution": {
        "description": "after 90 days, nothing available",
        "window_days": None,
        "resolution": "none"
    }
}
