# matcher.py
import requests
from rapidfuzz import fuzz

TEAM_DB = []


def load_teams():
    global TEAM_DB
    res = requests.get(
        "https://bgmi-overlay-ukfd.vercel.app/api/teams",
        timeout=10
    )
    res.raise_for_status()
    TEAM_DB = res.json()

def normalize(text: str) -> str:
    if not text:
        return ""

    return (
        text.lower()
        .replace("@", "a")
        .replace("0", "o")
        .replace("1", "l")
        .replace("|", "l")
        .replace("!", "l")
        .replace("7", "t")
        .replace("5", "s")
        .replace("8", "b")
        .replace("$", "s")
        .replace("€", "e")
        .replace(" ", "")
        .strip()
    )


def similarity(a: str, b: str) -> float:

    if not a or not b:
        return 0.0

    return fuzz.partial_ratio(a, b) / 100.0



def match_player(ocr_tokens):


    best_match = None
    best_score = 0.0

    for token in ocr_tokens:
        t = normalize(token)

        if len(t) < 3:
            continue

        for team in TEAM_DB:
            team_name = team.get("teamName", "")
            team_image = team.get("teamImage", "")
            team_color = team.get("teamColor", "")

            for player in team.get("players", []):
                player_name = player.get("playerName", "")
                player_image = player.get("playerImage", "")

                p = normalize(player_name)

                score = similarity(t, p)

                # Tune threshold here if needed
                if score >= 0.75 and score > best_score:
                    best_score = score
                    best_match = {
                        "playerName": player_name,
                        "teamName": team_name,
                        "teamImage": team_image,
                        "playerImage": player_image,
                        "color": team_color,
                        "score": round(score, 3),
                        "matchedToken": token,
                    }

    return best_match