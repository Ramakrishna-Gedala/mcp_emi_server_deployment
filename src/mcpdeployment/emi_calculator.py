"""
FastMCP-powered EMI calculator server that proxies tool invocations to the
underlying REST API exposed by the EMI backend service.

Each tool prepares a payload, delegates the HTTP request to `_post`, and returns
the backend's JSON response (or a structured error on failure).
"""

import os

from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables (e.g. EMI_API_BASE_URL) from a `.env` file when present.
load_dotenv()

# Base URL of the EMI backend; defaults to the local development server.
BASE_URL = os.getenv("EMI_API_BASE_URL", "http://localhost:8000/api")

mcp = FastMCP("emi-calculator-server")


def _post(path: str, payload: Dict[str, Any]):
    """
    Submit a JSON payload to the configured backend endpoint and return the parsed response.

    Args:
        path: API route appended to `BASE_URL`.
        payload: Dictionary serialized into the request body.

    Returns:
        Parsed JSON data from the backend on success, otherwise an error dictionary.
    """
    url = f"{BASE_URL}{path}"

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": "backend_error", "details": str(e), "payload": payload}


# ------------------------------------------------------
# TOOL 1: Calculate EMI
# ------------------------------------------------------
@mcp.tool()
def calculate_emi(
    principal: float,
    interestRate: float,
    tenure: int,
    calculation_method: str = "reducing",
) -> Dict:
    """
    Calculate the equated monthly instalment (EMI) for a single loan scenario.

    Args:
        principal: Loan amount.
        interestRate: Annual interest rate expressed in percent (e.g. 9.5).
        tenure: Total tenure in months.
        calculation_method: Backend calculation strategy (for example, \"reducing\").

    Returns:
        Backend JSON payload containing EMI details or an error structure.
    """
    payload = {
        "principal": principal,
        "annual_rate": interestRate,
        "tenure_months": tenure,
        "calculation_method": calculation_method,
    }

    return _post("/calculate-emi", payload)


# ------------------------------------------------------
# TOOL 2: Generate EMI Schedule
# ------------------------------------------------------
@mcp.tool()
def calculate_schedule(
    principal: float,
    interestRate: float,
    tenure: int,
    calculation_method: str = "reducing",
) -> Dict:
    """
    Retrieve the amortization schedule for a loan configuration.

    Args:
        principal: Loan amount.
        interestRate: Annual interest rate expressed in percent (e.g. 9.5).
        tenure: Total tenure in months.
        calculation_method: Backend calculation strategy (for example, \"reducing\").

    Returns:
        Backend JSON payload describing the amortization schedule or an error structure.
    """
    payload = {
        "principal": principal,
        "annual_rate": interestRate,
        "tenure_months": tenure,
        "calculation_method": calculation_method,
    }

    return _post("/amortization-schedule", payload)


# ------------------------------------------------------
# TOOL 3: Compare Multiple Loans
# ------------------------------------------------------
@mcp.tool()
def compare_loans(
    scenarios: List[Dict[str, Any]],
    calculation_method: str = "reducing",
) -> Dict:
    """
    Compare EMI outputs for multiple loan scenarios in a single API call.

    Args:
        scenarios: List of loan dictionaries with keys
            `name`, `principal`, `interestRate`, and `tenure`.
            Optional key `calculation_method` overrides the default.
        calculation_method: Default strategy applied when a scenario omits it.

    Returns:
        Backend JSON payload with comparison results or an error structure.
    """
    formatted_scenarios: List[Dict[str, Any]] = []

    # Normalize each scenario to the backend payload contract.
    for scenario in scenarios:
        formatted_scenarios.append(
            {
                "name": scenario.get("name"),
                "principal": scenario["principal"],
                "annual_rate": scenario["interestRate"],
                "tenure_months": scenario["tenure"],
                "calculation_method": scenario.get(
                    "calculation_method", calculation_method
                ),
            }
        )

    payload = {"scenarios": formatted_scenarios}
    return _post("/compare-loans", payload)


# ------------------------------------------------------
# TOOL 4: EMI With Prepayment
# ------------------------------------------------------
@mcp.tool()
def calculate_with_prepayment(
    principal: float,
    interestRate: float,
    tenure: int,
    prepayment_amount: float,
    prepayment_frequency: str,
    prepayment_start_month: int,
    calculation_method: str = "reducing",
) -> Dict:
    """
    Calculate EMI outcomes when regular prepayments reduce the outstanding principal.

    Args:
        principal: Loan amount.
        interestRate: Annual interest rate expressed in percent (e.g. 9.5).
        tenure: Total tenure in months.
        prepayment_amount: Amount paid on each prepayment event.
        prepayment_frequency: Frequency descriptor (for example, \"monthly\" or \"quarterly\").
        prepayment_start_month: Month number when prepayment begins (1-indexed).
        calculation_method: Backend calculation strategy (for example, \"reducing\").

    Returns:
        Backend JSON payload capturing EMI adjustments, duration changes, and savings or an error structure.
    """
    payload = {
        "principal": principal,
        "annual_rate": interestRate,
        "tenure_months": tenure,
        "prepayment_amount": prepayment_amount,
        "prepayment_frequency": prepayment_frequency,
        "prepayment_start_month": prepayment_start_month,
        "calculation_method": calculation_method,
    }

    return _post("/calculate-with-prepayment", payload)


# ------------------------------------------------------
# Start Server
# ------------------------------------------------------
if __name__ == "__main__":
    print("Starting EMI Calculator MCP Server...")
    mcp.run()
