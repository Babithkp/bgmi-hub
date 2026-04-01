import requests
import re
from rapidfuzz import fuzz

TEAM_DB = []
TEAM_SLOT_MAP = {}


# ==============================
# LOAD DATA
# ==============================
def load_teams():
    global TEAM_DB, TEAM_SLOT_MAP

    res = requests.get(
        "https://bgmi-overlay-ukfd.vercel.app/api/teams",
        timeout=10
    )
    res.raise_for_status()

    TEAM_DB = res.json()

    # Fast slot lookup
    TEAM_SLOT_MAP = {
        team.get("slotNumber"): team
        for team in TEAM_DB
    }


# ==============================
# NORMALIZE TEXT (PLAYER MATCH)
# ==============================
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


# ==============================
# PLAYER MATCH (PRIORITY)
# ==============================
def match_player(ocr_tokens):
    best_match = None
    best_score = 0.0

    for token in ocr_tokens:
        t = normalize(token)

        if len(t) < 3:
            continue

        for team in TEAM_DB:
            for player in team.get("players", []):
                player_name = player.get("playerName", "")
                p = normalize(player_name)

                score = similarity(t, p)

                if score >= 0.75 and score > best_score:
                    best_score = score
                    best_match = {
                        "playerName": player_name,
                        "playerImage": player.get("playerImage"),
                        "teamName": team.get("teamName"),
                        "teamImage": team.get("teamImage"),
                        "color": team.get("teamColor"),
                        "slotNumber": team.get("slotNumber"),
                        "score": round(score, 3),
                        "matchedToken": token,
                    }

    return best_match


# ==============================
# CLEAN OCR NUMBER
# ==============================
def clean_token(token: str) -> str:
    return (
        token.replace("O", "0")
        .replace("o", "0")
        .replace("I", "1")
        .replace("l", "1")
        .replace("S", "5")
        .replace("B", "8")
        .replace("G", "6")
    )


def extract_numbers(tokens):
    numbers = []

    for token in tokens:
        if not token:
            continue

        token = str(token).strip()
        token = clean_token(token)

        if token.isdigit():
            numbers.append(int(token))
            continue

        found = re.findall(r"\d+", token)

        for num in found:
            try:
                numbers.append(int(num))
            except:
                pass

    return numbers


# ==============================
# SLOT MATCH (FALLBACK)
# ==============================
def match_slot(ocr_tokens):
    numbers = extract_numbers(ocr_tokens)

    for num in numbers:
        team = TEAM_SLOT_MAP.get(num)

        if team:
            return {
                "slotNumber": num,
                "teamName": team.get("teamName"),
                "teamImage": team.get("teamImage"),
                "color": team.get("teamColor"),
            }

    return None


# ==============================
# FINAL MATCH (HYBRID)
# ==============================
def match_all(slot_tokens, text_tokens):
    """
    Priority:
    1. Player match (OCR2)
    2. Slot match (OCR1)
    """

    # 🔥 Try player first
    player_match = match_player(text_tokens)
    if player_match:
        print("PLAYER MATCH ✅")
        return player_match

    # 🔁 fallback to slot
    slot_match = match_slot(slot_tokens)
    if slot_match:
        print("SLOT MATCH 🔁")
        return slot_match

    return None