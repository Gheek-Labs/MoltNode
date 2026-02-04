import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

agent = None

def get_agent():
    """Lazy-load the agent to avoid import errors at startup."""
    global agent
    if agent is None:
        from providers import get_provider
        from minima_agent import MinimaAgent
        provider = get_provider()
        agent = MinimaAgent(provider)
    return agent

@app.route("/")
def index():
    """Serve the chat interface."""
    return render_template("chat.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return jsonify({"error": "Message required"}), 400
        
        agent = get_agent()
        response = agent.chat(user_message)
        
        return jsonify({
            "response": response,
            "provider": agent.provider.get_info()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/reset", methods=["POST"])
def reset():
    """Reset conversation history."""
    try:
        agent = get_agent()
        agent.reset()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/command", methods=["POST"])
def direct_command():
    """Execute a direct Minima command (restricted to safe read-only commands)."""
    try:
        data = request.get_json()
        command = data.get("command", "").strip()
        
        if not command:
            return jsonify({"error": "Command required"}), 400
        
        from minima_agent import execute_command, is_safe_command
        
        if not is_safe_command(command):
            return jsonify({
                "error": "Command not allowed via direct API. Use the chat interface for transaction commands.",
                "status": False
            }), 403
        
        result = execute_command(command)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/provider", methods=["GET"])
def get_provider_info():
    """Get current LLM provider info."""
    try:
        agent = get_agent()
        return jsonify(agent.provider.get_info())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
