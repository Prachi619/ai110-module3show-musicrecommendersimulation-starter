import csv
import math
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

# --- Algorithm Recipe -------------------------------------------------------
# Numeric features are scored by closeness to the user's target using a Gaussian
# curve: small gaps cost little, large gaps cost a lot (see _closeness).
# Weights below only apply when the user profile supplies that key; the final
# score is normalized by the weights that were actually used (range 0.0 - 1.0).
NUMERIC_WEIGHTS: Dict[str, float] = {
    "energy": 0.35,
    "instrumentalness": 0.25,
    "acousticness": 0.10,
    "valence": 0.05,
}
MOOD_WEIGHT = 0.20
GENRE_WEIGHT = 0.05
# Smaller sigma = pickier. At 0.25 a gap of 0.1 keeps ~92% of the points, 0.3 keeps ~49%, 0.6 keeps ~6%.
CLOSENESS_SIGMA = 0.25
# An exact mood match earns full credit; a mood in the same family earns this share.
MOOD_FAMILY_CREDIT = 0.6

MOOD_FAMILIES: Dict[str, str] = {
    "chill": "calm", "relaxed": "calm", "focused": "calm", "peaceful": "calm",
    "happy": "upbeat", "uplifting": "upbeat", "euphoric": "upbeat",
    "passionate": "upbeat", "confident": "upbeat",
    "intense": "intense", "angry": "intense", "energetic": "intense",
    "moody": "dark", "melancholy": "dark", "sad": "dark", "bittersweet": "dark",
    "nostalgic": "warm", "romantic": "warm",
}


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float = 0.0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: Optional[float] = None


def _closeness(song_value: float, target: float) -> float:
    """Return 1.0 for an exact match, falling toward 0 as the gap grows (Gaussian)."""
    gap = song_value - target
    return math.exp(-(gap ** 2) / (2 * CLOSENESS_SIGMA ** 2))


def _profile_to_prefs(user: UserProfile) -> Dict:
    """Convert a UserProfile into the dict format used by score_song."""
    prefs = {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "acousticness": 0.8 if user.likes_acoustic else 0.15,
    }
    if user.target_valence is not None:
        prefs["valence"] = user.target_valence
    return prefs


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs for a user, ranked by score."""
        prefs = _profile_to_prefs(user)
        ranked = sorted(
            self.songs,
            key=lambda s: score_song(prefs, asdict(s))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a one-line explanation of why a song scored as it did."""
        score, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return f"score {score:.2f}: " + "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv into a list of dicts with numeric fields converted to int/float."""
    int_fields = {"id"}
    float_fields = {"energy", "tempo_bpm", "valence", "danceability",
                    "acousticness", "instrumentalness"}
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for key in int_fields:
                row[key] = int(row[key])
            for key in float_fields:
                if row.get(key) not in (None, ""):
                    row[key] = float(row[key])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song from 0 to 1 against user preferences and return it with point-by-point reasons."""
    earned = 0.0
    possible = 0.0
    reasons: List[str] = []

    for feature, weight in NUMERIC_WEIGHTS.items():
        if feature not in user_prefs or feature not in song:
            continue
        closeness = _closeness(float(song[feature]), float(user_prefs[feature]))
        earned += weight * closeness
        possible += weight
        reasons.append(f"{feature} {song[feature]:.2f} vs target {user_prefs[feature]:.2f} "
                       f"(+{weight * closeness * 100:.1f})")

    if "mood" in user_prefs and "mood" in song:
        possible += MOOD_WEIGHT
        if song["mood"] == user_prefs["mood"]:
            earned += MOOD_WEIGHT
            reasons.append(f"mood '{song['mood']}' matches (+{MOOD_WEIGHT * 100:.1f})")
        else:
            wanted = MOOD_FAMILIES.get(user_prefs["mood"])
            if wanted is not None and wanted == MOOD_FAMILIES.get(song["mood"]):
                credit = MOOD_WEIGHT * MOOD_FAMILY_CREDIT
                earned += credit
                reasons.append(f"mood '{song['mood']}' is in the same family as "
                               f"'{user_prefs['mood']}' (+{credit * 100:.1f})")

    if "genre" in user_prefs and "genre" in song:
        possible += GENRE_WEIGHT
        if song["genre"] == user_prefs["genre"]:
            earned += GENRE_WEIGHT
            reasons.append(f"genre '{song['genre']}' matches (+{GENRE_WEIGHT * 100:.1f})")

    score = earned / possible if possible else 0.0
    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort best first, and return the top k as (song, score, explanation)."""
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]
