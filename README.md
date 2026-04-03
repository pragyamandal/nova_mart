# NovaMart Customer Service Environment

An OpenEnv-compatible RL environment for training agents to resolve customer service issues under real policy constraints.

## Overview

This environment simulates a customer service agent at NovaMart, a fictional electronics retailer. The novel mechanic is **constraint negotiation** — the agent must find the best possible resolution when the obvious answer is blocked by policy. Unlike existing environments, NovaMart features a ranked solution space where multiple valid resolutions exist with different quality scores. The agent must investigate, reason about policies, and navigate ambiguity to maximize customer satisfaction within the boundaries of what is actually allowed.

## Environment Description

- **Simulated company**: NovaMart sells consumer electronics (phones, laptops, earbuds, smartwatches)
- **8 available tools**: `lookup_order`, `check_policy`, `verify_defect`, `check_loyalty`, `process_refund`, `issue_store_credit`, `process_exchange`, `escalate_to_manager`
- **3 policy paths**:
  - **Standard return** — 30-day window, full refund, item must be unopened
  - **Defective item** — 90-day window, full refund, defect must be verified
  - **Loyalty goodwill** — 60-day window, store credit, silver or gold tier only

## Tasks

| Task | Difficulty | Description | Max Steps |
|------|-----------|-------------|-----------|
| `easy_refund` | Easy | Standard return within 30 days, all tools work perfectly | 10 |
| `defect_resolution` | Medium | Defect claim outside standard return window, agent must find the defect policy path | 10 |
| `loyalty_negotiation` | Hard | Gold tier customer outside all standard windows, ambiguous defect claim, multiple constrained resolution paths | 10 |

## Observation Space

| Field | Type | Description |
|-------|------|-------------|
| `customer_id` | string | Unique identifier for the customer |
| `customer_name` | string | Full name of the customer |
| `issue_description` | string | The customer's complaint or request |
| `order_id` | string | Order being discussed |
| `days_since_purchase` | integer | Number of days since the order was placed |
| `customer_tier` | string | Loyalty tier: standard, silver, or gold |
| `conversation_history` | list[string] | All messages exchanged so far |
| `available_actions` | list[string] | Actions the agent can take this step |
| `step_number` | integer | Current step in the episode |
| `max_steps` | integer | Maximum steps allowed for this task |
| `tools_used` | list[string] | Tools the agent has already called |
| `last_tool_result` | dict | Output from the most recent tool call |

## Action Space

| Action Type | Description |
|-------------|-------------|
| `lookup_order` | Retrieve order details by order ID |
| `check_policy` | Check eligibility under a specific return policy |
| `verify_defect` | Verify whether a product defect is confirmed |
| `check_loyalty` | Check customer loyalty tier and goodwill eligibility |
| `process_refund` | Process a monetary refund for an order |
| `issue_store_credit` | Issue store credit to the customer's account |
| `process_exchange` | Exchange the product for a different item |
| `escalate_to_manager` | Escalate the case to a manager for review |
| `respond_to_customer` | Send a message to the customer without taking a tool action |

## Reward Structure

- **step_reward**: Given at every step, not just at the end of the episode
- **resolution_score**: How close the agent's resolution is to the optimal outcome (0.0–1.0)
- **tool_use_score**: Whether the right tool was called with correct parameters
- **communication_score**: Quality of the customer-facing message
- **penalty**: Deductions for incorrect actions
  - −0.3 for choosing the wrong resolution type
  - −0.4 for promising a refund the customer is not eligible for

## Setup and Usage

### Run with Docker

```bash
docker build -t novamart-env .
docker run -p 7860:7860 novamart-env
```

### Run inference

```bash
cp .env.example .env
# Edit .env with your API credentials
python inference.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `API_BASE_URL` | LLM API endpoint (OpenAI-compatible) |
| `MODEL_NAME` | Model identifier |
| `HF_TOKEN` | Your API key |

## Baseline Scores

| Task | Expected Score Range |
|------|---------------------|
| `easy_refund` | 0.7 – 1.0 |
| `defect_resolution` | 0.5 – 0.8 |
| `loyalty_negotiation` | 0.3 – 0.6 |
