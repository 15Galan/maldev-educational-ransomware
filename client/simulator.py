import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import timedelta


SERVER_URL = os.environ.get(
    "TRAINING_SERVER",
    "http://127.0.0.1:5000"
)

COUNTDOWN_SECONDS = 8 * 60 * 60

LAB_DIRECTORY = (
    Path.home()
    / "Desktop"
    / "Ransomware-Training-Lab"
)


def banner():
    os.system("cls" if os.name == "nt" else "clear")

    print("=" * 70)
    print("                 RANSOMWARE TRAINING")
    print("=" * 70)
    print()
    print("             *** SIMULATION ONLY ***")
    print()
    print("This program does NOT encrypt real files.")
    print("This program does NOT delete real files.")
    print()
    print("=" * 70)
    print()


def create_lab_files():
    LAB_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    files = {
        "training_document.txt":
            "This is a harmless ransomware-training document.\n",

        "training_document.pdf":
            "SIMULATED PDF CONTENT - TRAINING ONLY\n",

        "training_photo.jpg":
            "SIMULATED JPG CONTENT - TRAINING ONLY\n",

        "training_document.docx":
            "SIMULATED DOCX CONTENT - TRAINING ONLY\n"
    }

    for filename, content in files.items():
        path = LAB_DIRECTORY / filename

        if not path.exists():
            path.write_text(
                content,
                encoding="utf-8"
            )


def simulate_encryption():
    print("[*] Starting simulated encryption...")
    print()

    files = list(LAB_DIRECTORY.iterdir())

    for path in files:

        if not path.is_file():
            continue

        print(
            f"[SIMULATION] Encrypting: "
            f"{path.name}"
        )

        time.sleep(1)

    print()
    print("[!] Simulation completed.")
    print()
    print(
        "No actual encryption was performed."
    )


def get_challenge():
    try:
        response = requests.get(
            f"{SERVER_URL}/challenge",
            timeout=5
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:

        print()
        print("[!] Unable to contact training server.")
        print(f"[!] Error: {exc}")
        print()

        return None


def validate_token(token):
    try:

        response = requests.post(
            f"{SERVER_URL}/validate",
            json={
                "token": token
            },
            timeout=5
        )

        return response.status_code == 200

    except requests.RequestException:

        return False


def countdown(seconds):
    while seconds > 0:

        hours, remainder = divmod(
            seconds,
            3600
        )

        minutes, secs = divmod(
            remainder,
            60
        )

        print(
            f"\rTIME REMAINING: "
            f"{hours:02d}:{minutes:02d}:{secs:02d}",
            end="",
            flush=True
        )

        time.sleep(1)
        seconds -= 1


def show_recovery_screen(challenge):
    print()
    print("=" * 70)
    print("                 YOUR FILES ARE LOCKED")
    print("=" * 70)
    print()
    print(
        "This is a ransomware-response training exercise."
    )
    print()
    print(
        "Your objective is to obtain the recovery token"
    )
    print(
        "from the training infrastructure."
    )
    print()
    print(
        "The exercise timeout is 8 hours."
    )
    print()
    print("=" * 70)
    print()

    public_key = challenge.get(
        "public_key",
        {}
    )

    print("[RSA PUBLIC KEY]")
    print()
    print(
        f"n = {public_key.get('n')}"
    )
    print(
        f"e = {public_key.get('e')}"
    )

    print()
    print("=" * 70)
    print()


def main():

    banner()

    print(
        "[*] Preparing isolated training environment..."
    )

    create_lab_files()

    print(
        f"[*] Training files created in:"
    )

    print(
        f"    {LAB_DIRECTORY}"
    )

    print()

    time.sleep(2)

    simulate_encryption()

    challenge = get_challenge()

    if challenge is None:
        input(
            "Press ENTER to exit..."
        )
        return

    show_recovery_screen(
        challenge
    )

    print(
        "Enter the recovery token."
    )

    print(
        "For this lab, the default token is:"
    )

    print(
        "TRAINING-RANSOM-2026"
    )

    print()

    start = time.time()

    while True:

        elapsed = int(
            time.time() - start
        )

        remaining = max(
            0,
            COUNTDOWN_SECONDS - elapsed
        )

        if remaining <= 0:

            print()
            print()
            print(
                "[!] TRAINING TIMEOUT"
            )

            print(
                "[SIMULATION] "
                "The training files would now be considered lost."
            )

            print()
            break

        token = input(
            "Recovery token: "
        ).strip()

        if validate_token(token):

            print()
            print("=" * 70)
            print("                 RECOVERY SUCCESSFUL")
            print("=" * 70)
            print()
            print(
                "The ransomware incident has been"
            )
            print(
                "successfully resolved."
            )
            print()
            print(
                "[+] Files remain available because"
            )
            print(
                "    this is a safe simulation."
            )
            print()
            print("=" * 70)

            break

        print()
        print(
            "[!] Invalid recovery token."
        )
        print(
            "[!] Try again."
        )
        print()

    input(
        "\nPress ENTER to exit..."
    )


if __name__ == "__main__":
    main()
