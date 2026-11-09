# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent to try to break my recommender, and then to fix the weak spots it found. This took several steps in a row: invent tricky listener profiles, run them, read the results, change the scoring, and run everything again to compare.


**Prompts used:**

 "Define at least three distinct user preference dictionaries... suggest 'adversarial' or 'edge case' user profiles"
- "apply them and re-run these five profiles to compare"
- "explain why 'Storm Runner' ranked first for my 'Deep intense rock' profile... Show the point contribution of each rule and tell me what would change the ranking if I doubled the genre weight"
**What did the agent generate or change?**

`src/main.py`: three everyday profiles (Pop / happy, Chill lofi, Deep intense rock) and five edge-case profiles:
  - Conflict: wants sad songs but very high energy
  - Unknown labels: asks for k-pop, which is not in the catalog
  - Indifferent: 0.5 on everything, no labels
  - Impossible: energy 1.0 and acousticness 1.0 together
  - Label vs sound: asks for classical but with a loud, euphoric sound
- It also changed `main()` so every profile runs in one go and prints a clean list with the score and the reasons.
- `src/recommender.py`: after the first run showed that genre and mood bonuses could beat songs that actually sounded right, the agent lowered the genre weight (to 5) and the mood weight (to 20), and replaced the straight-line closeness rule with a Gaussian curve (sigma 0.25) so large gaps are punished much more.

**What did you verify or fix manually?**

Read every top 5 against my own ear. For example, Library Rain first for chill lofi and Storm Runner first for deep rock both made sense. Caught a wrong suggestion The agent first suggested "squared distance" to punish big gaps. Running the numbers showed it is more lenient, not stricter (a gap of 0.5 scores 0.25 instead of 0.5), so we switched to the Gaussian curve.
Re-ran the tests. All 9 tests still pass after the changes.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
