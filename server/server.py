from flask import Flask, jsonify, request
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import base64
import hashlib
import os
import time

app = Flask(__name__)

COUNTDOWN_SECONDS = 8 * 60 * 60

PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

PUBLIC_KEY = PRIVATE_KEY.public_key()

START_TIME = time.time()

EXERCISE_TOKEN = os.environ.get(
    "EXERCISE_TOKEN",
    "TRAINING-RANSOM-2026"
)

EXPECTED_HASH = hashlib.sha256(
    EXERCISE_TOKEN.encode()
).hexdigest()


@app.get("/health")
def health():
    return jsonify({
        "status": "online",
        "exercise": "ransomware-training"
    })


@app.get("/challenge")
def challenge():
    elapsed = int(time.time() - START_TIME)
    remaining = max(0, COUNTDOWN_SECONDS - elapsed)

    public_numbers = PUBLIC_KEY.public_numbers()

    return jsonify({
        "exercise": "RANSOMWARE TRAINING",
        "remaining_seconds": remaining,
        "public_key": {
            "n": str(public_numbers.n),
            "e": public_numbers.e
        }
    })


@app.post("/validate")
def validate():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request"
        }), 400

    submitted = data.get("token", "")

    submitted_hash = hashlib.sha256(
        submitted.encode()
    ).hexdigest()

    if submitted_hash == EXPECTED_HASH:
        return jsonify({
            "success": True,
            "message": "TRAINING SUCCESSFUL",
            "status": "SOLVED"
        })

    return jsonify({
        "success": False,
        "message": "Invalid recovery token",
        "status": "ACTIVE"
    }), 401


if __name__ == "__main__":
    print("=" * 60)
    print(" RANSOMWARE TRAINING SERVER")
    print("=" * 60)
    print()
    print("Training token configured.")
    print("Countdown: 8 hours")
    print()
    print("Server listening on:")
    print("http://0.0.0.0:5000")
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
