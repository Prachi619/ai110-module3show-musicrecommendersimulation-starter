# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This project is a small content-based music recommender. It reads 20 songs from `data/songs.csv`, scores each one against a listener's taste profile (genre, mood, energy, valence, acousticness, instrumentalness), ranks them, and prints the top 5 with the reasons behind every score. It runs from the command line with `python -m src.main`.

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
- popularity (0–100, how well known the song is; optional in scoring, only used when the profile sets a `popularity` target)
- release_year (e.g. 1988 to 2023; optional, scored when the profile sets a `release_year` target)
- speechiness (0–1, spoken words such as rap versus singing or instrumentals; optional)
- mood_tags (detailed tags such as `late-night|study|cozy`, 3 per song; optional, scored by how many of the profile's wanted tags the song has)
- tempo_bpm and danceability (loaded but not scored, because they largely duplicate)

UserProfile features

Each UserProfile stores:

- favorite_genre (string)
- favorite_mood (string)
- target_energy (0–1, the energy level the user wants)
- likes_acoustic (bool; maps to a target acousticness of high or low)
- target_valence (0–1, optional, defaults to none so the existing tests still work)
- target_popularity (0–1, optional; 0 = hidden gems, 1 = big hits)
- target_release_year (a year such as 1995, optional)
- target_speechiness (0–1, optional)
- wanted_tags (a list such as `["late-night", "study"]`, optional)

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
| Popularity (optional) | 5 | 5 × closeness, only when the profile sets a popularity target. Song popularity is divided by 100 first. |
| Speechiness (optional) | 5 | 5 × closeness, only when the profile sets a speechiness target. |
| Release year (optional) | 5 | 5 × closeness, only when the profile sets a year. Years are scaled across 1980 to 2025, so 10 years apart is a gap of about 0.22. |
| Tags (optional) | 10 | 10 × (wanted tags the song has ÷ wanted tags). A song with 1 of 2 wanted tags earns 5. |

Closeness is a bell curve: `exp(−gap² / (2 × 0.25²))`. A gap of 0.1 keeps about 92% of the points, 0.3 keeps about 49%, and 0.6 keeps about 6%, so big mismatches are punished hard.

The total is divided by the points that were possible to give a score from 0 to 1. The six core rules add up to 100. If a profile leaves out a key, that rule is skipped and the score is normalized over the rules that remain. That is why the four optional rules (popularity, speechiness, release year and tags) do not change results for profiles that don't set them.

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

The same run also prints the chill lofi, deep intense rock and four adversarial profiles. Top-3 output for three of them is shown under Experiments.

---

## Experiments Tried

I ran 8 profiles: 3 everyday (pop / happy, chill lofi, deep intense rock) and 5 adversarial. Here is the top 3 for three of them (pop / happy is shown above).

**Chill lofi**

```
========================================================================
  CHILL LOFI
  Profile: genre=lofi, mood=chill, energy=0.35, valence=0.6, acousticness=0.8, instrumentalness=0.85
========================================================================

1. Library Rain - Paper Lanterns                          Score: 0.99
   lofi | chill
     * energy 0.35 vs target 0.35 (+35.0)
     * instrumentalness 0.90 vs target 0.85 (+24.5)
     * acousticness 0.86 vs target 0.80 (+9.7)
     * valence 0.60 vs target 0.60 (+5.0)
     * mood 'chill' matches (+20.0)
     * genre 'lofi' matches (+5.0)

2. Midnight Coding - LoRoom                               Score: 0.98
   lofi | chill
     * energy 0.42 vs target 0.35 (+33.7)
     * instrumentalness 0.85 vs target 0.85 (+25.0)
     * acousticness 0.71 vs target 0.80 (+9.4)
     * valence 0.56 vs target 0.60 (+4.9)
     * mood 'chill' matches (+20.0)
     * genre 'lofi' matches (+5.0)

3. Focus Flow - LoRoom                                    Score: 0.91
   lofi | focused
     * energy 0.40 vs target 0.35 (+34.3)
     * instrumentalness 0.88 vs target 0.85 (+24.8)
     * acousticness 0.78 vs target 0.80 (+10.0)
     * valence 0.59 vs target 0.60 (+5.0)
     * mood 'focused' is in the same family as 'chill' (+12.0)
     * genre 'lofi' matches (+5.0)
```

**Deep intense rock**

```
========================================================================
  DEEP INTENSE ROCK
  Profile: genre=rock, mood=intense, energy=0.92, valence=0.45, acousticness=0.1, instrumentalness=0.1
========================================================================

1. Storm Runner - Voltline                                Score: 1.00
   rock | intense
     * energy 0.91 vs target 0.92 (+35.0)
     * instrumentalness 0.08 vs target 0.10 (+24.9)
     * acousticness 0.10 vs target 0.10 (+10.0)
     * valence 0.48 vs target 0.45 (+5.0)
     * mood 'intense' matches (+20.0)
     * genre 'rock' matches (+5.0)

2. Gym Hero - Max Pulse                                   Score: 0.91
   pop | intense
     * energy 0.93 vs target 0.92 (+35.0)
     * instrumentalness 0.03 vs target 0.10 (+24.0)
     * acousticness 0.05 vs target 0.10 (+9.8)
     * valence 0.77 vs target 0.45 (+2.2)
     * mood 'intense' matches (+20.0)

3. Iron Requiem - Black Cathedral                         Score: 0.84
   metal | angry
     * energy 0.97 vs target 0.92 (+34.3)
     * instrumentalness 0.10 vs target 0.10 (+25.0)
     * acousticness 0.06 vs target 0.10 (+9.9)
     * valence 0.22 vs target 0.45 (+3.3)
     * mood 'angry' is in the same family as 'intense' (+12.0)
```

**Conflict: wants "sad" songs but very high energy**

```
========================================================================
  CONFLICT (SAD BUT HIGH ENERGY)
  Profile: genre=folk, mood=sad, energy=0.9, valence=0.25, acousticness=0.5, instrumentalness=0.1
========================================================================

1. Storm Runner - Voltline                                Score: 0.66
   rock | intense
     * energy 0.91 vs target 0.90 (+35.0)
     * instrumentalness 0.08 vs target 0.10 (+24.9)
     * acousticness 0.10 vs target 0.50 (+2.8)
     * valence 0.48 vs target 0.25 (+3.3)

2. Iron Requiem - Black Cathedral                         Score: 0.66
   metal | angry
     * energy 0.97 vs target 0.90 (+33.7)
     * instrumentalness 0.10 vs target 0.10 (+25.0)
     * acousticness 0.06 vs target 0.50 (+2.1)
     * valence 0.22 vs target 0.25 (+5.0)

3. Rooftop Lights - Indigo Parade                         Score: 0.63
   indie pop | happy
     * energy 0.76 vs target 0.90 (+29.9)
     * instrumentalness 0.05 vs target 0.10 (+24.5)
     * acousticness 0.35 vs target 0.50 (+8.4)
     * valence 0.81 vs target 0.25 (+0.4)
```

**How the outputs differ.**

- **Pop / happy vs chill lofi:** no songs in common. Pop wants loud, upbeat, vocal tracks (Sunrise City). Lofi wants quiet, acoustic, instrumental ones (Library Rain). Energy and instrumentalness are doing their job.
- **Pop / happy vs deep intense rock:** both want high energy, so they share Fuego Nights, Concrete Crown and Gym Hero. Rock puts guitar-driven Storm Runner and metal Iron Requiem first, because of mood and a lower valence target.
- **Conflict profile:** it gets loud songs (Storm Runner, Iron Requiem) and no sad ones. The sound numbers outvote the word "sad".
- **Why Gym Hero keeps appearing:** it is a pop song with the right sound for happy pop. Only its "intense" mood is wrong, which costs it 20 points and drops it to 5th. For the rock profile its mood matches, so it rises to 2nd.

**Other experiments.**

- **Weight shift (double energy, halve genre):** the top song was the same for all 8 profiles. Positions 2 to 5 changed for 7 of them.
- **Remove the mood check:** the top song was the same for 7 of 8 profiles. Iron Requiem moved ahead of Gym Hero for the rock listener.
- **Double the genre weight (5 to 10):** no ranking change. Only one song per genre gets the bonus.
- **Popularity attribute:** I added a 0–100 `popularity` column and an optional `popularity` target. I ran the pop / happy profile three ways: no popularity target, a "hits" target (0.95) and a "hidden gems" target (0.15). The top 5 were the same songs in the same order each time. Only the scores moved (for example Sunrise City: 1.00, 0.99 and 0.95). Popularity is worth only 5 points, so it nudges scores but doesn't reorder a list the other features already agree on. Since the most popular songs (Fuego Nights 92, Gym Hero 90, Concrete Crown 85) are also the "central" ones that show up everywhere, popularity bias is something to watch if its weight is raised.
- **New attributes (release year, speechiness, tags):** I added three more song attributes. Two new profiles use them. Top 3 for each:

**Late-night throwback** (wants the tags `late-night` and `heartbreak`, a song from around 1990, and almost no spoken words)

```
========================================================================
  LATE-NIGHT THROWBACK (TAGS + RELEASE YEAR)
  Profile: genre=blues, mood=bittersweet, energy=0.4, valence=0.4, acousticness=0.7, instrumentalness=0.3, release_year=1990, speechiness=0.03, tags=['late-night', 'heartbreak']
========================================================================

1. Smoke and Mirrors - Delta Slim                         Score: 0.98
   blues | bittersweet
     * energy 0.48 vs target 0.40 (+33.3)
     * instrumentalness 0.25 vs target 0.30 (+24.5)
     * acousticness 0.66 vs target 0.70 (+9.9)
     * valence 0.38 vs target 0.40 (+5.0)
     * speechiness 0.05 vs target 0.03 (+5.0)
     * release_year 1988 vs target 1990 (+4.9)
     * mood 'bittersweet' matches (+20.0)
     * genre 'blues' matches (+5.0)
     * tags matched: heartbreak, late-night (2 of 2) (+10.0)

2. Hollow Pines - Ash and Ember                           Score: 0.75
   folk | sad
     * energy 0.30 vs target 0.40 (+32.3)
     * instrumentalness 0.15 vs target 0.30 (+20.9)
     * acousticness 0.93 vs target 0.70 (+6.5)
     * valence 0.20 vs target 0.40 (+3.6)
     * speechiness 0.03 vs target 0.03 (+5.0)
     * release_year 1992 vs target 1990 (+4.9)
     * mood 'sad' is in the same family as 'bittersweet' (+12.0)
     * tags matched: heartbreak (1 of 2) (+5.0)

3. Nocturne in Blue - Elena Varga                         Score: 0.57
   classical | melancholy
     * energy 0.22 vs target 0.40 (+27.0)
     * instrumentalness 0.97 vs target 0.30 (+0.7)
     * acousticness 0.95 vs target 0.70 (+6.1)
     * valence 0.18 vs target 0.40 (+3.4)
     * speechiness 0.02 vs target 0.03 (+5.0)
     * release_year 1985 vs target 1990 (+4.5)
     * mood 'melancholy' is in the same family as 'bittersweet' (+12.0)
     * tags matched: heartbreak, late-night (2 of 2) (+10.0)
```

**Summer party** (wants the tags `party` and `summer`, a 2022 release, and a popular song)

```
========================================================================
  SUMMER PARTY (POPULARITY + TAGS)
  Profile: genre=edm, mood=euphoric, energy=0.9, valence=0.85, acousticness=0.1, instrumentalness=0.05, release_year=2022, speechiness=0.1, popularity=0.9, tags=['party', 'summer']
========================================================================

1. Neon Overdrive - Pulse Theory                          Score: 0.88
   edm | euphoric
     * energy 0.96 vs target 0.90 (+34.0)
     * instrumentalness 0.35 vs target 0.05 (+12.2)
     * acousticness 0.03 vs target 0.10 (+9.6)
     * valence 0.88 vs target 0.85 (+5.0)
     * popularity 0.88 vs target 0.90 (+5.0)
     * speechiness 0.05 vs target 0.10 (+4.9)
     * release_year 2023 vs target 2022 (+5.0)
     * mood 'euphoric' matches (+20.0)
     * genre 'edm' matches (+5.0)
     * tags matched: party, summer (2 of 2) (+10.0)

2. Fuego Nights - Luna Calle                              Score: 0.88
   latin | passionate
     * energy 0.84 vs target 0.90 (+34.0)
     * instrumentalness 0.02 vs target 0.05 (+24.8)
     * acousticness 0.20 vs target 0.10 (+9.2)
     * valence 0.86 vs target 0.85 (+5.0)
     * popularity 0.92 vs target 0.90 (+5.0)
     * speechiness 0.10 vs target 0.10 (+5.0)
     * release_year 2020 vs target 2022 (+4.9)
     * mood 'passionate' is in the same family as 'euphoric' (+12.0)
     * tags matched: party, summer (2 of 2) (+10.0)

3. Sunrise City - Neon Echo                               Score: 0.83
   pop | happy
     * energy 0.82 vs target 0.90 (+33.3)
     * instrumentalness 0.02 vs target 0.05 (+24.8)
     * acousticness 0.18 vs target 0.10 (+9.5)
     * valence 0.84 vs target 0.85 (+5.0)
     * popularity 0.82 vs target 0.90 (+4.8)
     * speechiness 0.05 vs target 0.10 (+4.9)
     * release_year 2021 vs target 2022 (+5.0)
     * mood 'happy' is in the same family as 'euphoric' (+12.0)
     * tags matched: summer (1 of 2) (+5.0)
```

What the new attributes did. In the throwback profile, Hollow Pines and Nocturne in Blue appear in the top 3. Before the tags were added, these two songs were never recommended for any profile. Nocturne in Blue scores 0.57 mostly because it has both wanted tags (+10) and a release year close to 1990, even though its instrumentalness (0.97 vs a target of 0.30) is far off. That is good for variety, but it also shows tags can pull in a song that doesn't sound right. In the summer-party profile, Neon Overdrive and Fuego Nights tie at 0.88: both have both tags, and the release year and popularity are nearly the same. Without the extra attributes there would be little to separate them.

- **Closeness rule:** I replaced a straight-line gap with a bell curve. This fixed the conflict profile, which used to put a low-energy sad folk song first.

---

## Limitations and Risks

- It only works on a tiny catalog of 20 made-up songs.
- A few songs (Fuego Nights, Sunrise City, Concrete Crown) show up for most listeners. 
- It does not understand lyrics, language, artists or release year.
- Mood tags can mislead. Gym Hero is "intense," so it can beat a better-sounding metal song for a rock listener.
- An impossible request still gets a confident score.

More detail is in the [Model Card](model_card.md).

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Recommenders turn data into predictions by scoring and sorting. The weights decide what the user sees. When I changed the mood and genre weights and the closeness rule. Even simple point-adding felt like a real recommendation, mostly because every pick came with reasons but it also felt arbitrary in what lbale assigned for mood were. Bias or unfairness could show up, small, hand-made data and hand-set weights shape results. A few "central" songs fit many users, so they crowd out the rest. Mood tags are labels someone chose, so a wrong tag can push a song up or down. 
