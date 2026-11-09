# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

A small recommender that matches songs to a listener's "vibe."

---

## 2. Intended Use  

**Goal.** The system suggests songs a listener might like. It does this by comparing each song's sound and labels to the listener's taste.

**What it gives.** It returns the top 5 songs. Each one has a score from 0 to 1 and a list of reasons.

**What it assumes** It assumes the listener can describe their taste in numbers. For example, "energy 0.8" or "acoustic 0.2". It assumes one taste per person.

**Intended use** This is for learning. It helps show how recommenders turn data into scores. Not the best for practical use as it fails to accomidate scale and many other factors.

**Not intended for.**
- Real music apps with real users
- Making decisions about artists
- Guessing anything about a person from their taste
- Catalogs much bigger than 20 songs. The weights were tuned for this small file

---

## 3. How the Model Works  

Think of the recommender as a judge who gives every song in the catalog a mark out of 100 for how well it fits what you said you like, then hands you the songs with the highest marks.

**What it looks at.** For each song it considers how energetic it is, how instrumental it is (no vocals versus vocals), how acoustic it sounds, how positive or upbeat it feels (valence), its mood label, and its genre. If the listener asks for them, it can also check four extras: popularity (how well known a song is), release year, speechiness (how much of the song is spoken words, like rap) and detailed tags such as "late-night" or "study". It ignores tempo and danceability, since they mostly repeat what energy already tells it.

**What you tell it.** You give it a target for each of those: a favorite genre, a favorite mood, and how energetic, acoustic, instrumental and upbeat you want the music to be.

**How a song earns points.** For the numbers, a song gets more points the *closer* it is to your target, not the higher it is. If you want calm music at an energy of 0.35, a song at 0.40 scores nearly full marks, and a song at 0.90 scores close to nothing. Small gaps cost little, but the penalty grows quickly as the gap widens. Mood and genre work like bonuses. A matching mood earns 20 points, and a mood that is close in spirit (chill, relaxed and focused count as one family) earns 12. A matching genre earns 5.

| What is checked | Points possible |
|---|---|
| Energy | 35 |
| Instrumentalness | 25 |
| Mood | 20 |
| Acousticness | 10 |
| Genre | 5 |
| Valence | 5 |
| Popularity (only if the listener sets a target) | 5 |
| Speechiness (only if the listener sets a target) | 5 |
| Release year (only if the listener sets a year) | 5 |
| Tags (only if the listener names tags) | 10 |

Tags work a little differently from the numbers. A song earns points for each tag the listener asked for that it has. If the listener wants two tags and the song has one, it earns half.

**Turning marks into a list.** The score for one song never looks at any other song. Once every song has a mark, the system sorts them from best to worst and shows the top few. Each one comes with a list of reasons, such as "energy 0.35 vs target 0.35 (+30.0)", so you can see exactly why it was picked.

**What I changed from the starter.** The starter only had empty placeholders. I added reading the song file, the scoring rule, the ranking step and the reasons. I also made mood count for more than genre, because with 17 genres across 20 songs a genre match usually points at only one song, while moods are shared by several. I added an instrumentalness feature, and I let moods in the same family earn partial credit.

---

## 4. Data  

**Size.** The catalog is `data/songs.csv`. It has 20 songs.

**Features per song.** Title, artist, genre, mood, energy, tempo, valence, danceability, acousticness, instrumentalness, popularity, release year, speechiness and tags. The numbers run from 0 to 1, except tempo (beats per minute), popularity (0 to 100) and release year (1985 to 2023). Each song has three tags, like "late-night|study|focus".

**What is in it.** There are 17 genres. Only lofi (3 songs) and pop (2 songs) appear more than once. There are 16 moods. Chill, happy and intense appear more than once. Most others appear once.

**What I changed.** The starter had 10 songs. I added 10 more with new genres and moods. I also added the instrumentalness column.

**Limits.**
- The songs are made up and the numbers were set by hand. They are not measured from real audio.
- Twenty songs is very small.
- There is no language or lyrics.
- Popularity, release year, speechiness and tags were all set by hand. They are not measured from real audio or real listeners.
- Tags help variety, but they can pull in a song that doesn't sound right. In one test, Nocturne in Blue (classical) scored well for a "late-night heartbreak" listener because it has both tags, even though it is far from their instrumental target.
- Popularity is a made-up number, not real listening data. The most popular songs (Fuego Nights, Gym Hero, Concrete Crown) are also the ones that show up for most listeners.
- Some tastes are missing. There is little world music, no spoken word, and few mid-energy songs.

---

## 5. Strengths  

Overall, the system did a good job matching songs to different listener preferences. Quiet and loud listeners received very different recommendations, with chill lofi and deep rock sharing no songs. The top recommendations also made sense, with Storm Runner ranking first for rock and Library Rain for lofi. Another thing that worked well was the explanations behind each recommendation, making it easy to understand why a song received its score. The system also handled missing mood and genre labels without crashing by relying on sound features instead. The results generally matched my expectations, especially with Sunrise City ranking first for pop/happy listeners.

---

## 6. Limitations and Bias 

The biggest weakness I noticed was that the same few songs kept appearing in different recommendations. After testing eight profiles, Fuego Nights appeared in six of them, while four songs never appeared at all. This happens because energy and instrumentalness make up most of the score, so songs with similar sound features tend to rank well for many listeners. This can create a filter bubble where listeners keep seeing the same songs instead of discovering new ones. There were also issues with mood labels not always matching the sound, scores appearing confident even when a request was impossible, and missing features like lyrics, language, tempo, and artist. Overall, the system works, but it could use more variety and better ways to understand what listeners actually want.
---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Three everyday listeners: Pop / happy (upbeat, high energy, vocals), Chill lofi (quiet, acoustic, no vocals) and Deep intense rock (loud, high energy, dark). Five tricky listeners built to confuse it: Conflict (wants "sad" songs but very high energy), Unknown labels (asks for k-pop, which are not in the catalog), Indifferent (middle value on everything, no genre or mood), Impossible (maximum energy and maximum acoustic at the same time) and Label vs sound (asks for "classical" but with a loud, euphoric sound). For each one I looked at whether the top 5 matched what a person would expect, and checked the reasons the system printed.

**What the three everyday profiles got:**

- Pop / happy: Sunrise City, Rooftop Lights, Fuego Nights, Concrete Crown, Gym Hero.
- Chill lofi: Library Rain, Midnight Coding, Focus Flow, Spacewalk Thoughts, Coffee Shop Stories.
- Deep intense rock: Storm Runner, Gym Hero, Iron Requiem, Fuego Nights, Concrete Crown.

**Comparing the profiles.**

Comparing the different listener profiles showed how much their preferences affect the recommendations. Pop/happy and chill lofi had no songs in common because one prefers loud, upbeat music while the other prefers quiet, acoustic songs. Pop and rock shared a few songs because they both favor high energy, but the order changed based on mood and genre. The conflict profile was also interesting because it prioritized loud music over the sad mood, showing that sound features can outweigh mood preferences. For profiles with unknown labels, the system still found similar-sounding songs, even though the scores were lower. Listeners with no strong preferences received calmer, middle-energy songs. I also noticed that impossible requests could still receive high confidence scores even when no song actually matched all their preferences. Overall, the comparisons showed that the system does a good job separating different music tastes, but it still has trouble when preferences conflict or when the song catalog does not have a good match.

**What surprised me.**

One thing I noticed was how often "Gym Hero" appeared for Happy Pop fans. Since it matches the pop genre and has a similar upbeat sound to Sunrise City, it still ranks in the top five even though its mood is tagged as intense instead of happy. In the rock profile, it actually moves up to second because that mood fits better. I also noticed that some songs, like Fuego Nights, appear in many different profiles, while four songs never appear at all. Another important takeaway is that higher scores do not necessarily mean a perfect match, just the best option available. Finally, removing mood from the scoring barely changed the results, with the top song staying the same for 7 out of 8 profiles.

---

## 8. Future Work  

If I continued this project, I would focus on adding more variety to the top five recommendations so the same songs or artists do not keep appearing. I would also add confidence warnings when a song does not fully match what the user is looking for. Another improvement would be allowing multiple taste profiles, such as study and workout, while adding more songs in different moods and genres. Finally, I would let users edit their recommendations and use those changes to better understand their preferences.
---

## 9. Personal Reflection  

My biggest takeaway was how much small changes to the scoring weights can affect song recommendations but also how muaced these judgments can be. AI helped with planning, coding, and testing, but its suggestions still needed to be checked. For example, it suggested using squared distance, but after testing, we realized it would actually be more lenient, so we switched to a Gaussian curve(not something I am famialar with but it is something I can search up and test that it worked better). I was surprised that a simple point system could still give recommendations that felt accurate, like putting "Library Rain" first for a lofi listener. However, it also showed how easily a song like Gym Hero could appear for the wrong reasons. If I continued this project, I would add more variety, confidence warnings, and songs to test the system. I would also experiment with collaborative filtering using fake users' likes and skips to improve recommendations.
