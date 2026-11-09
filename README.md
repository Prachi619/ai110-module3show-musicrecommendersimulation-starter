# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms use two kinds of signals to predict reccomendations. Collaborative filtering learns from the behavior of many users (likes, skips, playlist adds, listening time) and Content-based filtering compares the attributes of songs (tempo, energy, mood, audio embeddings) against what you already enjoy.

 My version is a small, content-based recommender, so it has no other user data to learn from. It prioritizes closeness to the user's taste, a song scores well when its energy and valence are near the user's target, not simply when they are large. Mood is the strongest categorical signal because it is the most direct label for a song's vibe.Genre counts for less, because it is sparse in this small catalog. Acousticness acts as a tiebreaker.

Song features
- id, title, artist (identification only, not used for scoring)
- genre (categorical, small weight)
- mood (categorical, large bonus on an exact match)
- energy (0–1, main numeric feature)
- valence (0–1, musical positivity; separates "intense and dark" from "intense and upbeat")
- acousticness (0–1, texture tiebreaker)
- instrumentalness (0–1, vocal vs. instrumental; separates acoustic songs with vocals from acoustic instrumentals)
- tempo_bpm and danceability (loaded but not scored, because they largely duplicate)

UserProfile features

Each UserProfile stores:

- favorite_genre (string)
- favorite_mood (string)
- target_energy (0–1, the energy level the user wants)
- likes_acoustic (bool; maps to a target acousticness of high or low)
- target_valence (0–1, optional, defaults to none so the existing tests still work)

 Algorithm Recipe

Scoring Rule (one song, 100 points possible):

| Rule | Points | How it's earned |
|---|---|---|
| Energy | 35 | 35 × closeness |
| Instrumentalness | 25 | 25 × closeness |
| Mood | 20 | Full points for an exact match; 12 (60%) if the moods are in the same family (e.g. chill / relaxed / focused) |
| Acousticness | 10 | 10 × closeness |
| Genre | 5 | Full points for an exact match, otherwise 0 |
| Valence | 5 | 5 × closeness |

Closeness is a bell curve: `exp(−gap² / (2 × 0.25²))`. A gap of 0.1 keeps about 92% of the points, 0.3 keeps about 49%, and 0.6 keeps about 6%, so big mismatches are punished hard.

The total is divided by 100 to give a score from 0 to 1. If a profile leaves out a key, that rule is skipped and the score is normalized over the rules that remain.

Ranking Rule (all songs): score every song in the catalog, sort from highest to lowest, and return the top k with a short explanation of why each was chosen.

Why these weights. A common starting point is genre = 2.0 and mood = 1.0. I flipped it: mood counts more than genre. In this catalog there are 17 genres across 20 songs, so a genre match usually singles out one song, while moods repeat and describe the listening "vibe" more directly. Energy gets the most points because it has the widest, most useful spread. Instrumentalness separates acoustic songs with vocals from acoustic instrumentals, which energy and acousticness can't do. Valence gets the fewest points because its range in this data is narrow, so it barely separates songs.


Expected biases

- Labels can outweigh sound
 Mood and genre are worth 25 of 100 points, so a song with the right tags but the wrong feel can still win in a close race. Genre is also close to a pick this one song bonus, with 17 genres across 20 songs. The reverse risk also exists: with numbers dominating, a "sad but high energy" user now gets no sad songs in the top 5, because high-energy matches beat the mood label.
- Exact tags are brittle Mood families are judgment, and a mislabeled song like Gym Hero (intense pop) can outrank a better fit like Iron Requiem for a rock listener.
- Calm and sad look alike Only valence tells them apart, and it carries just 5 points, so melancholy songs can show up in a "chill" list.
- Small, hand-made data and one profile per user The weights are tuned to 20 authored songs, and there is no collaborative signal, so it keeps recommending the same style.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default pop / happy profile:

```
Loaded songs: 20

========================================================================
  POP / HAPPY (DEFAULT)
  Profile: genre=pop, mood=happy, energy=0.8, valence=0.8, acousticness=0.2, instrumentalness=0.05
========================================================================

1. Sunrise City - Neon Echo                               Score: 1.00
   pop | happy
     * energy 0.82 vs target 0.80 (+34.9)
     * instrumentalness 0.02 vs target 0.05 (+24.8)
     * acousticness 0.18 vs target 0.20 (+10.0)
     * valence 0.84 vs target 0.80 (+4.9)
     * mood 'happy' matches (+20.0)
     * genre 'pop' matches (+5.0)

2. Rooftop Lights - Indigo Parade                         Score: 0.93
   indie pop | happy
     * energy 0.76 vs target 0.80 (+34.6)
     * instrumentalness 0.05 vs target 0.05 (+25.0)
     * acousticness 0.35 vs target 0.20 (+8.4)
     * valence 0.81 vs target 0.80 (+5.0)
     * mood 'happy' matches (+20.0)

3. Fuego Nights - Luna Calle                              Score: 0.86
   latin | passionate
     * energy 0.84 vs target 0.80 (+34.6)
     * instrumentalness 0.02 vs target 0.05 (+24.8)
     * acousticness 0.20 vs target 0.20 (+10.0)
     * valence 0.86 vs target 0.80 (+4.9)
     * mood 'passionate' is in the same family as 'happy' (+12.0)

4. Concrete Crown - Kid Meridian                          Score: 0.85
   hip hop | confident
     * energy 0.78 vs target 0.80 (+34.9)
     * instrumentalness 0.01 vs target 0.05 (+24.7)
     * acousticness 0.12 vs target 0.20 (+9.5)
     * valence 0.62 vs target 0.80 (+3.9)
     * mood 'confident' is in the same family as 'happy' (+12.0)

5. Gym Hero - Max Pulse                                   Score: 0.74
   pop | intense
     * energy 0.93 vs target 0.80 (+30.6)
     * instrumentalness 0.03 vs target 0.05 (+24.9)
     * acousticness 0.05 vs target 0.20 (+8.4)
     * valence 0.77 vs target 0.80 (+5.0)
     * genre 'pop' matches (+5.0)

------------------------------------------------------------------------
```

The same run also prints the chill lofi, intense rock and conflict profiles after this one.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



