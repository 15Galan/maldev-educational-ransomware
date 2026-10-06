import requests


SERVER = "http://127.0.0.1:8080"


def create_challenge():

    response = requests.post(
        f"{SERVER}/challenge",
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def get_status(challenge_id):

    response = requests.get(
        f"{SERVER}/challenge/{challenge_id}",
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def solve_challenge(challenge_id, key):

    response = requests.post(
        f"{SERVER}/solve",
        json={
            "challenge_id": challenge_id,
            "key": key
        },
        timeout=5
    )

    return response.json()
