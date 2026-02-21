# Minima Node - One-Click Bootstrap

## Overview
This project provides a one-click, agent-friendly setup for a headless Minima blockchain node. Its primary purpose is to offer a stable MxID identity system and a natural language chat interface for interaction. The node runs with RPC enabled for programmatic access. The vision is to simplify interaction with the Minima blockchain, making it accessible for developers and users through intuitive interfaces and stable identities, fostering broader adoption and innovative decentralized applications.

## User Preferences
- **Communication Style**: I prefer clear, concise language.
- **Workflow**: I value iterative development and detailed explanations.
- **Interaction**: Ask for confirmation before executing significant operations like transactions (`send`), `vault` operations, or `backup` procedures.
- **Codebase Changes**:
    - Do not modify files outside the designated project structure without explicit instruction.
    - Ensure all changes are well-documented and adhere to established coding practices.
    - Use the provided SDKs (`integration/node/minima-client.js` or `integration/python/minima_client.py`) for RPC interactions, avoiding raw `http.get()` calls due to known response formatting issues.
    - For on-chain data recording, use `./minima/record_data.sh --data "..."` to ensure proper hex encoding and transaction building.
    - When displaying balance, always use the `sendable` field from RPC responses, as `total` represents the token's max supply, not the wallet's actual balance.

## System Architecture
The system is designed around a Minima blockchain node, enhanced with several layers for usability and interaction.

### UI/UX Decisions
- **Chat Interface**: A natural language chat interface is available, accessible via a web browser on `localhost:5000`. It features a password-protected login page and uses configurable LLM providers.
- **Templates**: Reference implementations are provided for various use cases, including a Node.js web dashboard, a Node.js webhook listener, a Python bot, and a ROS2 bridge skeleton, demonstrating common integration patterns.

### Technical Implementations
- **Headless Minima Node**: The core is a Minima blockchain node running in a headless environment, enabling background operation without a graphical user interface.
- **RPC Interface**: The node exposes an RPC interface on `localhost:9005` for local programmatic interaction. All RPC responses are JSON formatted (`{"status": true/false, "response": ...}`).
- **MxID System**: A stable identity system (MxID) is integrated, allowing for reachable and persistent identities even with IP changes or node restarts. It includes a wizard for easy setup and primitives for identity management, signing, and verification.
- **MiniDapp System (MDS)**: A secure MiniDapp System is available on `port 9003`, protected by SSL and a high-entropy password. It allows for installation and management of decentralized applications.
- **Natural Language Chat Interface**: Built with Flask, this interface processes user queries using pluggable LLM providers (OpenAI, Anthropic, Ollama, Custom) and executes corresponding Minima commands after confirmation for sensitive operations.
- **Integration Kits**: Language-specific SDKs for Python and Node.js are provided to abstract RPC communication and handle response parsing, ensuring consistent and reliable interaction.
- **On-chain Records**: A dedicated script (`record_data.sh`) facilitates posting data onto the Minima blockchain, handling necessary encoding and transaction building.
- **Response Schemas**: Detailed machine-readable JSON schemas and human-readable documentation are provided for all RPC command responses, specifying field semantics, types, and agent warnings to ensure correct interpretation.

### Feature Specifications
- **One-Click Bootstrap**: A `bootstrap.sh` script automates the setup process, including downloading the Minima JAR and installing prerequisites.
- **Mandatory Bootstrap Sequence**: A defined 5-step sequence ensures proper node initialization, seed phrase backup, MxID setup, and peer connectivity verification.
- **Secure Chat Interface**: The chat interface is disabled by default and requires explicit enablement with a strong password. It includes rate limiting and input character limits for security.
- **MLS Auto-Detection**: The MxID setup intelligently detects if the node can act as its own MLS (Message Layer Security) based on network configuration.

### System Design Choices
- **Modularity**: The project structure separates concerns into distinct directories for chat, integration kits, and Minima node utilities.
- **Agent-Friendly Design**: The system prioritizes clear documentation, wrapper scripts, and SDKs to facilitate seamless interaction for automated agents.
- **Security by Default**: Features like the chat interface and MDS are secured by default (disabled or password-protected) and require explicit configuration for exposure.
- **Robust RPC Handling**: Specific guidelines are provided for handling RPC responses, including warnings about mixed data types, distinct field names for similar data, and the use of JSON parsers over regex for robustness.

## External Dependencies
- **Minima Blockchain Node**: The core dependency, with its JAR file downloaded on first run.
- **jq**: A lightweight and flexible command-line JSON processor, required for MxID initialization and other JSON parsing tasks.
- **curl**: Used by the bootstrap script for downloading the Minima JAR and other external resources.
- **OpenAI/Replit AI, Anthropic, Ollama**: Pluggable Large Language Model (LLM) providers for the natural language chat interface. The default is Replit AI (via OpenAI provider configuration).
- **Flask**: Python web framework used for the natural language chat interface.