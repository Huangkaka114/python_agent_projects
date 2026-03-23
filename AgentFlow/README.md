# AgentFlow: A Production-Ready LLM Agent System

![AgentFlow Architecture](https://placeholder.com/agentflow-arch)  <!-- 可替换为你的流程图路径 -->

# Project Overview

AgentFlow is a production-ready, engineering-standard LLM Agent built on LangGraph and LangChain. It focuses on structured tool calling, multi-role permission control, persistent memory, and full-link observability, enabling the agent to "think + act" rather than just "answer".

The core value of AgentFlow lies in solving the pain points of traditional LLM agents (such as random answers, no execution capability, and chaotic workflows) and realizing a closed-loop of "user instruction → AI reasoning → tool execution → result feedback", which is suitable for local operation automation, multi-scenario interaction, and enterprise-level AI application landing.

# Key Features

- **Structured Tool Calling**: Based on LLM native tool_calls, automatically match tools according to user needs, supporting plug-and-play tool expansion.

- **Multi-Role Permission Control (RBAC)**: Support three roles (admin/user/guest) with hierarchical tool access to ensure system security.

- **Persistent Memory**: Store short-term dialogue history and long-term user preferences, enabling personalized multi-turn interaction.

- **Full-Link Observability**: Provide workflow visualization and structured logging for easy debugging and operation tracing.

- **Modular Engineering Design**: Decouple configuration, core engine, tool pool, and storage to improve maintainability and scalability.

- **Global Exception Handling**: Capture model calling, tool execution, and file operation exceptions to ensure system stability.

- **Local Operation Support**: Integrate local system tools (screenshot, music playback, app opening) to realize "one-sentence operation".

# Tech Stack

- Core Framework: Python, LangGraph, LangChain

- LLM Integration: ChatOpenAI (compatible with domestic models such as Qwen)

- Configuration: YAML, python-dotenv

- Persistence: JSON, SQLite (optional)

- Observability: Logging, Graphviz (workflow visualization)

- Tool Encapsulation: LangChain Tool Decorator

# Project Architecture

AgentFlow adopts a 5-layer modular architecture, which is fully decoupled and easy to expand. The overall structure is as follows:

```plain text
【Entry Layer】          # Receive user input, load config and memory
        ↓
【Orchestration Layer】  # LangGraph workflow orchestration (Chat/Router/Permission/Tool)
        ↓
【Core Engine Layer】    # LLM reasoning, RBAC permission control, global exception handling
        ↓
【Capability Layer】     # Standardized pluggable tool pool
        ↓
【Storage Layer】        # Persistent memory, operation logs, local assets
```

## Layer Details

1. **Entry Layer**: Initialize project, load configuration files (.env, settings.yaml) and historical memory, receive user input.

2. **Orchestration Layer**: The core of the project, using LangGraph to build cyclic workflows, including chat nodes (LLM reasoning), router nodes (scenario recognition), permission nodes (access control), and tool nodes (execution).

3. **Core Engine Layer**: Provide core capabilities such as LLM structured tool calling, role-based permission verification, and global exception capture to ensure system security and stability.

4. **Capability Layer**: Standardize tool encapsulation, including local system tools, computing tools, and search tools, supporting rapid plug-and-play expansion.

5. **Storage Layer**: Store dialogue memory, user preferences, and operation logs to realize persistent memory and full-link tracing.

# Directory Structure

```plain text
agentflow/
├── config/                # Global configuration (decouple code and parameters)
│   ├── __init__.py
│   ├── settings.yaml       # Model, tool, permission, path configuration
│   └── .env                # API key, secret information
│
├── core/                   # Core engine (Agent brain)
│   ├── __init__.py
│   ├── graph.py            # LangGraph workflow orchestration
│   ├── llm.py              # LLM initialization and tool binding
│   └── memory.py           # Persistent memory (read/write)
│
├── engine/                 # Core business engine
│   ├── __init__.py
│   ├── permission.py       # RBAC permission verification
│   ├── router.py           # Scenario routing and condition judgment
│   └── exception.py         # Global exception handling
│
├── tools/                  # Standardized tool pool (pluggable)
│   ├── __init__.py
│   ├── base.py              # Tool base class and unified encapsulation
│   ├── system.py            # Local tools: screenshot, app opening, music
│   ├── compute.py           # Calculation tools
│   └── search.py            # Search tools
│
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── logger.py            # Structured logging
│   ├── visual.py            # Workflow visualization
│   └── common.py             # Common helper functions
│
├── storage/                # Persistent storage (auto-generated)
│   ├── memory.json          # Dialogue memory + user preferences
│   ├── logs/                # Running logs
│   └── assets/              # Local assets (screenshots, music)
│
├── prompts/                # Prompt templates
│   ├── __init__.py
│   ├── system.txt           # Main system prompt
│   └── role_prompts.yaml     # Multi-role prompts
│
├── main.py                 # Project entry
├── requirements.txt        # Dependencies
├── README.md               # Project documentation
└── .gitignore              # Ignored files
```

# Quick Start

## 1. Environment Preparation

1. Clone the repository:
        `git clone https://github.com/Huangkaka114/python_agent_projects/tree/dev/AgentFlow.git
cd agentflow`

2. Install dependencies:
`pip install -r requirements.txt`

3. Configure environment variables:


    - Copy `.env.example` to `.env` (create if not exists).

    - Fill in your LLM API key and base URL in `.env`.

4. Adjust configuration: Modify `config/settings.yaml` to set tool paths, role permissions, and model parameters according to your local environment.

## 2. Run the Project

```bash
python main.py
```

After running, enter user instructions (e.g., "Take a screenshot", "Play music", "Calculate 123*456") to experience the agent's capabilities.

# Key Modules Introduction

## 1. Persistent Memory

Implemented in `core/memory.py`, supporting reading and writing of dialogue history and user preferences, and automatically loading historical memory when the project starts.

## 2. Permission Control

Implemented in `engine/permission.py`, supporting three roles:
    Admin: Can call all tools (including local system tools).User: Can call non-high-risk tools (calculation, search).Guest: Only can use basic query functions.

## 3. Workflow Visualization

Run the visualization function in `utils/visual.py` to generate a workflow diagram (PNG format) to intuitively view the agent's running process.

## 4. Tool Expansion

To add a new tool, inherit the base class in `tools/base.py`, use the LangChain `@tool` decorator for encapsulation, and add the tool to the tool pool in `tools/__init__.py` (automatic registration).

# Engineering Highlights

- **Configuration Decoupling**: All parameters (model, tool, permission) are stored in configuration files, avoiding hard coding and facilitating maintenance.

- **Structured Logging**: Record tool calls, permission verifications, and model requests in detail, supporting full-link tracing and problem debugging.

- **Plug-and-Play Tools**: Standardized tool encapsulation, supporting rapid expansion without modifying core logic.

- **Stability Guarantee**: Global exception handling captures all possible exceptions to ensure the system does not crash.

# Future Roadmap

- Integrate more local tools (volume adjustment, file operation, email sending).

- Support more LLM models (compatible with open-source models such as LLaMA, ChatGLM).

- Add GUI interface to improve user interaction experience.

- Optimize memory mechanism (add memory compression to save tokens).

- Support multi-user management and role customization.

# Author

Huangkaka

Email: huangkaka_@outlook.com

GitHub: https://github.com/Huangkaka114/python_agent_projects/tree/dev/AgentFlow

# License

MIT License

