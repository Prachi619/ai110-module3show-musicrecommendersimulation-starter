"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from .recommender import load_songs, recommend_songs  # python -m src.main
except ImportError:
    from recommender import load_songs, recommend_songs  # python src/main.py


# Taste profile: target values for the features used in scoring.
# Categorical keys are matched exactly; numeric keys are matched by closeness.
TASTE_PROFILE = {
    "genre": "lofi",
    "mood": "chill",
    "energy": 0.35,
    "valence": 0.60,
    "acousticness": 0.80,
    "instrumentalness": 0.85,
}

# Default profile: upbeat pop listener.
POP_HAPPY_PROFILE = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.80,
    "valence": 0.80,
    "acousticness": 0.20,
    "instrumentalness": 0.05,
}

# Contrast profile used to check the system can tell opposite tastes apart.
INTENSE_ROCK_PROFILE = {
    "genre": "rock",
    "mood": "intense",
    "energy": 0.92,
    "valence": 0.45,
    "acousticness": 0.10,
    "instrumentalness": 0.10,
}


# Conflicting profile: a sad mood but very high energy. Shows which feature wins.
CONFLICT_PROFILE = {
    "genre": "folk",
    "mood": "sad",
    "energy": 0.90,
    "valence": 0.25,
    "acousticness": 0.50,
    "instrumentalness": 0.10,
}


STANDARD_PROFILES = {
    "Pop / happy (default)": POP_HAPPY_PROFILE,
    "Chill lofi": TASTE_PROFILE,
    "Deep intense rock": INTENSE_ROCK_PROFILE,
}

# Adversarial / edge-case profiles: built to try to trick the scoring logic.
ADVERSARIAL_PROFILES = {
    # Conflicting tastes: sad mood but very high energy.
    "Conflict (sad but high energy)": CONFLICT_PROFILE,
    # Labels that don't exist in the catalog: only the numbers can rank songs.
    "Unknown labels (k-pop / dreamy)": {
        "genre": "k-pop", "mood": "dreamy",
        "energy": 0.70, "valence": 0.70, "acousticness": 0.30, "instrumentalness": 0.10,
    },
    # Dead-center numbers, no labels: nothing should stand out.
    "Indifferent (all 0.5, no labels)": {
        "energy": 0.50, "valence": 0.50, "acousticness": 0.50, "instrumentalness": 0.50,
    },
    # Impossible combination: maximum energy AND maximum acousticness.
    "Impossible (energy 1.0 + acoustic 1.0)": {
        "genre": "pop", "mood": "happy",
        "energy": 1.0, "valence": 0.9, "acousticness": 1.0, "instrumentalness": 0.0,
    },
    # Labels that contradict the numbers: classical genre with a euphoric, high-energy sound.
    "Label vs sound (classical / euphoric)": {
        "genre": "classical", "mood": "euphoric",
        "energy": 0.95, "valence": 0.90, "acousticness": 0.05, "instrumentalness": 0.30,
    },
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, user_prefs in {**STANDARD_PROFILES, **ADVERSARIAL_PROFILES}.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)


WIDTH = 72


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Print one profile's top songs: title, score, and the reasons behind it."""
    print("\n" + "=" * WIDTH)
    print(f"  {name.upper()}")
    wanted = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print(f"  Profile: {wanted}")
    print("=" * WIDTH)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        # Left side: rank and title. Right side: the score, aligned in a column.
        left = f"{rank}. {song['title']} - {song['artist']}"
        print(f"\n{left:<{WIDTH - 14}}Score: {score:.2f}")
        print(f"   {song['genre']} | {song['mood']}")
        for reason in explanation.split("; "):
            print(f"     * {reason}")
    print("\n" + "-" * WIDTH)


if __name__ == "__main__":
    main()
