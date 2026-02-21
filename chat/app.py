import os
import sys
import time
import hmac
import secrets
import functools
from collections import defaultdict
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

ENABLE_CHAT = os.environ.get("ENABLE_CHAT", "false").lower() in ("true", "1", "yes")
CHAT_PASSWORD = os.environ.get("CHAT_PASSWORD", "")
CHAT_BIND = os.environ.get("CHAT_BIND", "127.0.0.1")
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
MAX_MESSAGE_LENGTH = 2000
RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_IPS = 10000

if not ENABLE_CHAT:
    print("")
    print("=" * 50)
    print("  Minima Chat is DISABLED (default)")
    print("=" * 50)
    print("")
    print("To enable, set the environment variable:")
    print("  ENABLE_CHAT=true")
    print("")
    print("You must also set a password:")
    print("  CHAT_PASSWORD=<your-password>")
    print("")
    print("Optional:")
    print("  CHAT_BIND=0.0.0.0    (to allow remote access)")
    print("  FLASK_DEBUG=true     (development only)")
    print("")
    sys.exit(0)

if not CHAT_PASSWORD:
    print("")
    print("ERROR: CHAT_PASSWORD is required when chat is enabled.")
    print("Set a strong password via environment variable or secrets.")
    print("")
    sys.exit(1)

if len(CHAT_PASSWORD) < 8:
    print("")
    print("ERROR: CHAT_PASSWORD must be at least 8 characters.")
    print("")
    sys.exit(1)

app = Flask(__name__)

_secret_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".session_secret")

def _get_session_secret():
    env_secret = os.environ.get("SESSION_SECRET")
    if env_secret:
        return env_secret
    if os.path.exists(_secret_file):
        with open(_secret_file, "r") as f:
            return f.read().strip()
    generated = secrets.token_hex(32)
    with open(_secret_file, "w") as f:
        f.write(generated)
    os.chmod(_secret_file, 0o600)
    return generated

app.secret_key = _get_session_secret()
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = CHAT_BIND == "0.0.0.0"

_rate_limits = defaultdict(list)

LOGIN_RATE_LIMIT_REQUESTS = 5
LOGIN_RATE_LIMIT_WINDOW = 300

_login_rate_limits = defaultdict(list)

def _get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"

def _prune_rate_limit_store(store, window):
    if len(store) > RATE_LIMIT_MAX_IPS:
        now = time.time()
        cutoff = now - window
        expired = [ip for ip, times in store.items() if not times or times[-1] < cutoff]
        for ip in expired:
            del store[ip]
        if len(store) > RATE_LIMIT_MAX_IPS:
            store.clear()

def _check_rate_limit(client_ip, bucket=None, max_requests=None, window=None):
    store = bucket if bucket is not None else _rate_limits
    limit = max_requests or RATE_LIMIT_REQUESTS
    win = window or RATE_LIMIT_WINDOW
    now = time.time()
    window_start = now - win
    _prune_rate_limit_store(store, win)
    store[client_ip] = [t for t in store[client_ip] if t > window_start]
    if len(store[client_ip]) >= limit:
        return False
    store[client_ip].append(now)
    return True

_session_token = secrets.token_hex(32)

def _generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]

def _validate_csrf_token():
    token = request.form.get("_csrf_token", "")
    expected = session.get("_csrf_token", "")
    if not expected or not hmac.compare_digest(token.encode(), expected.encode()):
        return False
    return True

app.jinja_env.globals["csrf_token"] = _generate_csrf_token

import logging
logger = logging.getLogger(__name__)

def _safe_error(e):
    logger.exception("Internal error")
    if FLASK_DEBUG:
        return str(e)
    return "An internal error occurred. Please try again."

def require_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if session.get("authenticated") != _session_token:
            if request.is_json:
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'self' https://*.replit.dev https://*.repl.co"
    )
    return response

agent = None

def get_agent():
    global agent
    if agent is None:
        from providers import get_provider
        from minima_agent import MinimaAgent
        provider = get_provider()
        agent = MinimaAgent(provider)
    return agent

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not _validate_csrf_token():
            return render_template("login.html", error="Invalid request. Please try again."), 403

        client_ip = _get_client_ip()
        if not _check_rate_limit(client_ip, bucket=_login_rate_limits,
                                  max_requests=LOGIN_RATE_LIMIT_REQUESTS,
                                  window=LOGIN_RATE_LIMIT_WINDOW):
            return render_template("login.html", error="Too many login attempts. Try again in a few minutes."), 429

        password = request.form.get("password", "")
        if hmac.compare_digest(password.encode("utf-8"), CHAT_PASSWORD.encode("utf-8")):
            session.clear()
            session["authenticated"] = _session_token
            session["_csrf_token"] = secrets.token_hex(32)
            return redirect(url_for("index"))
        return render_template("login.html", error="Incorrect password"), 401
    return render_template("login.html", error=None)

@app.route("/logout", methods=["POST"])
def logout():
    if not _validate_csrf_token():
        return redirect(url_for("login"))
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@require_auth
def index():
    return render_template("chat.html")

@app.route("/api/chat", methods=["POST"])
@require_auth
def chat():
    try:
        client_ip = _get_client_ip()
        if not _check_rate_limit(client_ip):
            return jsonify({"error": "Rate limit exceeded. Please wait before sending more messages."}), 429

        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Message required"}), 400

        if len(user_message) > MAX_MESSAGE_LENGTH:
            return jsonify({"error": f"Message too long. Maximum {MAX_MESSAGE_LENGTH} characters."}), 400

        agent = get_agent()
        response = agent.chat(user_message)

        return jsonify({
            "response": response,
            "provider": agent.provider.get_info()
        })

    except Exception as e:
        return jsonify({"error": _safe_error(e)}), 500

@app.route("/api/reset", methods=["POST"])
@require_auth
def reset():
    try:
        agent = get_agent()
        agent.reset()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": _safe_error(e)}), 500

@app.route("/api/command", methods=["POST"])
@require_auth
def direct_command():
    try:
        client_ip = _get_client_ip()
        if not _check_rate_limit(client_ip):
            return jsonify({"error": "Rate limit exceeded."}), 429

        data = request.get_json()
        command = data.get("command", "").strip()

        if not command:
            return jsonify({"error": "Command required"}), 400

        if len(command) > MAX_MESSAGE_LENGTH:
            return jsonify({"error": "Command too long."}), 400

        from minima_agent import execute_command, is_safe_command

        if not is_safe_command(command):
            return jsonify({
                "error": "Command not allowed via direct API. Use the chat interface for transaction commands.",
                "status": False
            }), 403

        result = execute_command(command)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": _safe_error(e)}), 500

@app.route("/api/provider", methods=["GET"])
@require_auth
def get_provider_info():
    try:
        agent = get_agent()
        return jsonify(agent.provider.get_info())
    except Exception as e:
        return jsonify({"error": _safe_error(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    print(f"Chat binding to {CHAT_BIND}:5000 (debug={FLASK_DEBUG})")
    app.run(host=CHAT_BIND, port=5000, debug=FLASK_DEBUG)
