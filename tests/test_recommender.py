from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_load_songs_reads_popularity_as_number():
    from src.recommender import load_songs

    songs = load_songs("data/songs.csv")
    assert len(songs) == 20
    assert all(isinstance(s["popularity"], float) for s in songs)
    assert all(0 <= s["popularity"] <= 100 for s in songs)


def test_popularity_target_prefers_the_closer_song():
    from src.recommender import score_song

    hit = {"title": "Hit", "popularity": 90.0}
    gem = {"title": "Gem", "popularity": 20.0}
    gem_seeker = {"popularity": 0.2}

    hit_score, _ = score_song(gem_seeker, hit)
    gem_score, reasons = score_song(gem_seeker, gem)
    assert gem_score > hit_score
    assert any("popularity" in r for r in reasons)


def test_load_songs_reads_new_attributes():
    from src.recommender import load_songs

    songs = load_songs("data/songs.csv")
    assert all(isinstance(s["release_year"], int) for s in songs)
    assert all(0 <= s["speechiness"] <= 1 for s in songs)
    assert all(len(s["mood_tags"].split("|")) >= 2 for s in songs)


def test_release_year_target_prefers_the_closer_year():
    from src.recommender import score_song

    old = {"release_year": 1988}
    new = {"release_year": 2022}
    throwback = {"release_year": 1990}

    old_score, _ = score_song(throwback, old)
    new_score, reasons = score_song(throwback, new)
    assert old_score > new_score
    assert "1988" in score_song(throwback, old)[1][0]


def test_tags_score_by_share_of_wanted_tags_matched():
    from src.recommender import score_song

    wanted = {"tags": ["late-night", "study"]}
    both = {"mood_tags": "late-night|study|focus"}
    one = {"mood_tags": "late-night|party|summer"}
    none = {"mood_tags": "party|summer|dance"}

    both_score, _ = score_song(wanted, both)
    one_score, _ = score_song(wanted, one)
    none_score, none_reasons = score_song(wanted, none)
    assert both_score > one_score > none_score
    assert none_reasons == []


def test_new_attributes_do_not_change_scores_when_unused():
    from src.recommender import score_song

    song = {"energy": 0.5, "release_year": 2000, "speechiness": 0.9, "mood_tags": "a|b|c"}
    score, reasons = score_song({"energy": 0.5}, song)
    assert score == 1.0
    assert len(reasons) == 1


def test_popularity_is_ignored_when_profile_has_no_target():
    from src.recommender import score_song

    song = {"energy": 0.5, "popularity": 95.0}
    _, reasons = score_song({"energy": 0.5}, song)
    assert not any("popularity" in r for r in reasons)
