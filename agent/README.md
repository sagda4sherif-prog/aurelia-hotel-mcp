# Aurelia Hotel MCP Agent Module

> An end-to-end implementation of an **MCP Client (Model Context Protocol)** designed to automate hotel recovery workflows, guest compensation approvals, and policy evaluations using **Google Gemini LLM**.

---

# Overview

The **Aurelia Hotel Recovery Agent** forms the intelligent client layer of the system. It connects to the Aurelia Hotel MCP Server via standard transports (**stdio** / **SSE**), negotiates capabilities dynamically, executes tools with defensive validation checks, listens for background notifications, and interfaces seamlessly with Gemini (`gemini-2.5-flash`) for multi-turn reasoning and tool invocation.

---

# System Architecture & Workflow

```text
+-----------------------------------------------------------------+
|                       Aurelia MCP Agent                         |
|  +-------------------+   +--------------------+  +------------+ |
|  | AureliaAgent      |   | Dynamic Catalog    |  | Gemini LLM | |
|  | (Orchestrator)    |---| Tools/Prompts/Res  |--| Reasoning  | |
|  +-------------------+   +--------------------+  +------------+ |
+-----------------------------------------------------------------+
                             |  ^
              MCP Protocol   |  | Notifications & Progress
         (Stdio / SSE Trans) v  |
+-----------------------------------------------------------------+
|                       Aurelia MCP Server                        |
|  +-------------------+   +--------------------+  +------------+ |
|  | SQLite Database   |---| Defensive Guards   |  | Resources  | |
|  | (hotel.db)        |   | (Business Logic)   |  | & Prompts  | |
|  +-------------------+   +--------------------+  +------------+ |
+-----------------------------------------------------------------+
```

---

# Module File Structure

```text
agent/
├── __init__.py          # Package marker
├── client.py            # AureliaAgent class & Gemini reasoning execution loop
├── config.py            # Environment configuration parser (.env handler)
├── demo.py              # 9-step end-to-end capability verification script
├── elicitation.py       # Human-in-the-loop approval callback handlers
├── handshake.py         # Protocol handshake & capability negotiation
├── helpers.py           # Tool helpers & schema transformers
├── notification.py      # Notification listener & dynamic catalog refresh
├── sampling.py          # Server-initiated sampling handlers
├── tools.py             # Tool catalog state management
└── transport.py         # stdio / SSE transport layer
```

---

# Core Features & Technical Highlights

## 1. Model Context Protocol (MCP)

- **Full Handshake Negotiation**
  - Verifies server protocol version (`2025-11-25`)
  - Negotiates supported capabilities dynamically
  - Feature-gates resources, prompts, notifications, and tool updates

- **Dual Transport Support**
  - `stdio`
  - `SSE`

- **Progress Tracking**
  - Receives `report_progress` notifications from long-running server operations.

---

## 2. Dynamic Tool Catalog & Role Escalation

- Notification-driven catalog refresh
- Supports `notifications/tools/list_changed`
- Automatically refreshes available tools after role promotion
- Uses background async tasks (`_pending_notification_tasks`) without blocking the agent

---

## 3. Defensive Business Logic

Implements client-side safety checks before tool execution, including:

- Rejecting invalid compensation amounts
- Preventing unauthorized approvals
- Avoiding duplicate approval requests
- Validating required tool parameters

---

## 4. Gemini LLM Reasoning Loop

Uses the Google GenAI SDK.

The agent:

- Converts MCP tools into Gemini Function Calling schemas
- Lets Gemini decide which tool(s) to invoke
- Executes the selected tools
- Returns tool outputs back to Gemini
- Produces the final natural-language response

---

# Requirements

## Python

```text
Python >= 3.10
```

## Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.5-flash
TRANSPORT_MODE=stdio
```

---

# Running the Demo

Run the complete end-to-end verification:

```bash
python -m agent.demo --auto
```

---

# 9-Step Demonstration Pipeline

| Step | Test | Purpose |
|------|------|---------|
| **1** | Capability Negotiation | Verifies negotiated server capabilities (tools, resources, prompts, notifications). |
| **2** | Baseline Tool Set | Displays the initial tool catalog available to the receptionist role. |
| **3** | Progress Tracking | Executes a long-running search operation and displays progress updates (33% → 66% → 100%). |
| **4** | Defensive Design | Attempts an invalid compensation approval to verify guard checks and error handling. |
| **5** | Role Escalation & Notifications | Promotes the user to manager, receives `tools/list_changed`, and refreshes the catalog automatically. |
| **6** | Compensation Approval | Executes a valid manager-only compensation approval request. |
| **7** | Gemini Reasoning Loop | Sends a natural-language request to Gemini, triggers tool selection, and generates the final response. |
| **8** | Resource Reading | Reads hotel policy resources through MCP Resource APIs. |
| **9** | Prompt Execution | Retrieves and executes a predefined prompt template for drafting a guest apology. |

---

# Robustness & Safety

- **AsyncExitStack**
  - Ensures graceful shutdown of transports and sessions.

- **Safe Notification Handling**
  - Notification callbacks tolerate optional SDK parameters.

- **Dynamic Capability Checks**
  - Agent never assumes optional MCP features are available.

- **SQLite Isolation**
  - Uses dedicated database connections and row factories.

- **Tool Catalog Refresh**
  - Keeps the available tool list synchronized with server-side role changes.

---

# Technologies

- Python
- Model Context Protocol (MCP)
- Google Gemini (`gemini-2.5-flash`)
- asyncio
- SQLite
- SSE / stdio transports
- JSON-RPC 2.0

## Transport Modes (Stdio vs. Streamable HTTP)

The Aurelia Agent supports two transport modes, configured via your `.env` file:

### 1. Stdio Mode (Default - Local Subprocess)
The agent launches the MCP server locally as a subprocess.
* **.env configuration:**
  ```env
  MCP_TRANSPORT=stdio

### 2. Streamable HTTP Mode (Remote / HTTP)
The agent connects to a running remote/HTTP MCP server.

Step 1: Run the server with HTTP transport:
```bash
python main.py  # configured with mcp.run(transport="streamable-http")
```
Step 2: Configure .env for the client:
```bash
MCP_TRANSPORT=http
MCP_SERVER_URL=[http://127.0.0.1:8000/mcp](http://127.0.0.1:8000/mcp)
```
Step 3: Run the demo/agent normally:
```bash
python -m agent.demo --auto
```