# First Setup EMI Calculator

<img width="867" height="326" alt="image" src="https://github.com/user-attachments/assets/ef879344-85b5-4699-86f5-be5d9e667f86" />

# MCP EMI Calculator Server

Lightweight MCP server that exposes loan EMI calculation endpoints to MCP clients (for example, Claude Desktop).

## Features

- STDIO-based FastMCP server that proxies to the REST backend
- Simple HTTP helper with JSON responses and 10 second timeout
- Configurable backend base URL via environment variables

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) for environment management (pip-compatible)

Install `uv` if you do not already have it:

- macOS/Linux:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Windows (PowerShell):
  ```powershell
  powershell -ExecutionPolicy Bypass -Command "iwr -useb https://astral.sh/uv/install.ps1 | iex"
  ```

## Quickstart (uv workflow)

1. Clone or download this repository.
2. From the project root, create a virtual environment (stored in `.venv` by default):
   ```bash
   uv venv
   ```
3. Activate the environment:
   ```bash
   source .venv/bin/activate      # macOS/Linux
   .venv\Scripts\Activate.ps1     # Windows (PowerShell)
   ```
4. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```
5. Create a `.env` file (if you do not already have one) with the backend base URL:
   ```
   EMI_API_BASE_URL=http://localhost:8000/api
   ```
6. Run the MCP server (communicates via STDIO):
   ```bash
   uv run python emi_calculator.py
   ```

## MCP Client Registration (Claude Desktop example)

Add to your `claude_desktop_config.json`:

```json
 "emiMcpServer": {
      "command": "uv",
      "args": [
        "--directory",
        "mcp_emi_server project path",
        "run",
        "emi_calculator.py"
      ]
    },
```

## Configuration (.env)

- `EMI_API_BASE_URL` — base URL of the backend EMI APIs (default: http://localhost:8000/api)

## Tools exposed

- `calculate_emi` — `{principal, interestRate, tenure, calculation_method?}` → EMI summary
- `calculate_schedule` — `{principal, interestRate, tenure, calculation_method?}` → amortization schedule
- `compare_loans` — `{scenarios: [{name, principal, interestRate, tenure, calculation_method?}, ...]}` → side-by-side comparison
- `calculate_with_prepayment` — `{principal, interestRate, tenure, prepayment_amount, prepayment_frequency, prepayment_start_month, calculation_method?}` → EMI with recurring prepayments

## Troubleshooting

- Ensure the backend EMI API is running and reachable.
- Check stderr logs for detailed errors.
