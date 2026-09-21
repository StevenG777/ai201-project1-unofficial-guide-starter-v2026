# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

This is a retrieval-augmented Q&A system built on the `campus_life` corpus — 88 short posts, each about one course, dorm, dining hall, or admin policy at a fictional university. It answers specific, factual questions a student would actually have: what step comes first in the grade appeal process, when you're allowed to declare a major, what a specific course's workload or assessment looks like, or what a specific dorm's laundry costs. It retrieves the most relevant post(s) for a question, refuses to answer when nothing in the corpus is close enough to be trustworthy, and otherwise answers using only what's in the retrieved posts, naming the source file it used.

## Chunking Strategy

**Chunk size:** One file = one chunk (whole-file chunking, not a fixed character count)
**Overlap:** 0

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->
Every file in campus_life is a short post about exactly one topic --> a single course, dorm, dining hall, or admin policy. I confirmed this by reading all 88 files in Milestone 1/3, not just assuming it. Because each file is already a self-contained thought, a fixed-size character window would risk cutting a sentence in half for no benefit.

So chunk_size/overlap don't apply here in the traditional sense: the natural unit is the file itself, and one file becomes exactly one chunk.

One known limitation: health_center.txt mixes urgent-care hours with a separate paragraph about counselling (two topics in one file). I left it as a single chunk anyway, since it's the only file in the corpus like this, and noted it here as a limitation rather than writing a special case just for one file.


## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `produced by: chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160.txt#0` — produced by: `chunker.py::split_documents`

```
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_hist_118_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0` — produced by: `chunker.py::split_documents`

```
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_innisfree_hall.txt#0` — produced by: `chunker.py::split_documents`

```
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.

For each one, ask: could someone answer a question using only this,
without reading what came before or after?
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** What is the first step in the grade appeal process

**Answer:**

```
The grade appeal starts with the instructor and must be raised within fifteen days of the grade posting (admin_grade_appeals.txt).

Sources retrieved: admin_grade_appeals.txt, course_engl_205.txt, course_engl_205_exams.txt, course_stat_150.txt, course_stat_150_exams.txt
```

**My relevance cutoff:** 0.55, top-k = 5

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

I ran all five of my test questions and all five OUT_OF_SCOPE questions through `app.py retrieve` and recorded the best (lowest) distance for each. The two groups came out cleanly separated, with no overlap:

- **In-corpus questions:** best distances of 0.228–0.280
- **Out-of-scope questions:** best distances of 0.825–0.934

That's a gap from about 0.28 to 0.82 — much wider than I expected. The starter's default of 0.6 already sits inside that gap and would work fine, but it's closer to the out-of-scope side than I'd like. I considered 0.3 at first, since it's just above my tightest in-corpus match (0.228), but that hugs the in-corpus edge too closely — a slightly awkward phrasing of a real, answerable question could easily land at 0.3–0.35 and get wrongly refused. Given the size of the actual gap, there was no reason to run that risk.

I decided to set my cutoff to **0.55**, which sits roughly in the middle: comfortably above every in-corpus best distance I measured (leaving room for a real question phrased more loosely than my five test questions) and comfortably below every out-of-scope distance.  

| Question | In corpus? | Best distance |
|---|---|---|
| What is the first step in the grade appeal process | Yes | 0.280 |
| When is the deadline to appeal your grade after grades are posted | Yes | 0.228 |
| What happen if you skip the instructor when appealing the grade | Yes | 0.252 |
| What is the last step in the grade appeal process | Yes | 0.270 |
| When is the earliest time you can declare your major | Yes | 0.242 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.934 |
| Who won the 1994 World Cup? | No | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844 |
| How do I write a for loop in Rust? | No | 0.896 |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I used ChatGPT to help design criteria 4 and 5. I started by asking what the actual point of writing a criterion is — it explained that a good criterion should target something the system might plausibly fail, so you can use it to drive a real improvement, not something it trivially passes. From there we talked through common chunking/overlap failure modes. My first instinct was purely mechanical fixed-size chunking, but ChatGPT gave me a counterexample showing a mechanically-cut chunk can fail to contain a semantically complete answer even if it contains the right characters — which meant I needed a semantic boundary, not just a character count. To define that boundary, I had it read through all 88 files in the corpus; it pointed out that each one follows the same shape — a short phrase describing the overall topic, followed by a paragraph on exactly one topic. We used that to define "on-topic" for criterion 4: content counts if a reader would recognize it as related to the current topic (exact wording or a paraphrase both count), as long as any factual claim can actually be pointed to in the source — opinions and judgments don't need that. I changed the wording of the criterion myself several times before settling on the final version with ChatGPT's help polishing it.

**2.** I asked Claude to write the body of `split_documents` in chunker.py, using the chunking/overlap strategy I'd already worked out from the criteria above. It came back with a working implementation, but the if/else structure didn't match the style of `fallback_split` already in the same file, so I rewrote that part myself to keep the two functions visually consistent. I then read through the logic and ran it against a few real files by hand to confirm the chunks it produced actually looked right before accepting it.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
