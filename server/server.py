from flask import Flask, jsonify, request
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path
from datetime import datetime, timezone
import base64
import json
import os
import uuid

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
KEY_DIR = BASE_DIR / "keys"
LOG_DIR = BASE_DIR / "logs"

PRIVATE_KEY_FILE = KEY_DIR / "private_key.pem"
PUBLIC_KEY_FILE = KEY_DIR / "public_key.pem"
LOG_FILE = LOG_DIR / "events.jsonl"

KEY_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def log_event(event, **data):
    entry = {
        "timestamp": utc_now(),
        "event": event,
        **data
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    print(json.dumps(entry))


def load_or_create_keys():
    if PRIVATE_KEY_FILE.exists() and PUBLIC_KEY_FILE.exists():
        with open(PRIVATE_KEY_FILE, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )

        with open(PUBLIC_KEY_FILE, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        return private_key, public_key

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_pem)

    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(public_pem)

    log_event("RSA_KEYPAIR_CREATED")

    return private_key, public_key


PRIVATE_KEY, PUBLIC_KEY = load_or_create_keys()

CHALLENGE_ID = f"CTF-{uuid.uuid4().hex[:8].upper()}"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "educational-ransomware-training",
        "challenge_id": CHALLENGE_ID
    })


@app.route("/challenge", methods=["GET"])
def challenge():
    public_pem = PUBLIC_KEY.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    log_event(
        "CHALLENGE_REQUESTED",
        challenge_id=CHALLENGE_ID
    )

    return jsonify({
        "challenge_id": CHALLENGE_ID,
        "algorithm": "AES-256-GCM",
        "key_protection": "RSA-OAEP-SHA256",
        "countdown_hours": 8,
        "server": "127.0.0.1:8080",
        "public_key": public_pem.decode()
    })


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    hostname = data.get("hostname", "unknown")
    username = data.get("username", "unknown")

    log_event(
        "CLIENT_REGISTERED",
        challenge_id=CHALLENGE_ID,
        hostname=hostname,
        username=username
    )

    return jsonify({
        "status": "registered",
        "challenge_id": CHALLENGE_ID
    })


@app.route("/event", methods=["POST"])
def event():
    data = request.get_json(silent=True) or {}

    event_name = data.get("event", "UNKNOWN")

    allowed_events = {
        "LAB_CREATED",
        "AES_KEY_GENERATED",
        "FILES_ENCRYPTED",
        "COUNTDOWN_STARTED",
        "UNLOCK_ATTEMPT",
        "FILES_DECRYPTED",
        "CHALLENGE_COMPLETED"
    }

    if event_name not in allowed_events:
        return jsonify({
            "error": "unsupported event"
        }), 400

    payload = {
        key: value
        for key, value in data.items()
        if key != "event"
    }

    log_event(
        event_name,
        challenge_id=CHALLENGE_ID,
        **payload
    )

    return jsonify({
        "status": "logged"
    })


@app.route("/unlock", methods=["POST"])
def unlock():
    data = request.get_json(silent=True) or {}

    supplied_key = data.get("key")

    if not supplied_key:
        return jsonify({
            "success": False,
            "error": "missing key"
        }), 400

    # CTF training validation.
    # The private RSA key is intentionally NOT returned by the server.
    #
    # For the exercise, the participant must obtain the private key
    # through the intended local CTF investigation path.

    try:
        supplied_key_bytes = base64.b64decode(supplied_key)

        serialization.load_pem_private_key(
            supplied_key_bytes,
            password=None
        )

        log_event(
            "UNLOCK_ATTEMPT",
            challenge_id=CHALLENGE_ID,
            result="VALID_PRIVATE_KEY"
        )

        return jsonify({
            "success": True,
            "challenge_id": CHALLENGE_ID
        })

    except Exception:
        log_event(
            "UNLOCK_ATTEMPT",
            challenge_id=CHALLENGE_ID,
            result="INVALID_KEY"
        )

        return jsonify({
            "success": False
        }), 403


if __name__ == "__main__":
    print("=" * 60)
    print("Educational Ransomware Training Server")
    print("=" * 60)
    print(f"Challenge ID : {CHALLENGE_ID}")
    print("Listening    : http://127.0.0.1:8080")
    print("=" * 60)

    log_event(
        "SERVER_STARTED",
        challenge_id=CHALLENGE_ID,
        address="127.0.0.1",
        port=8080
    )

    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False
    )
