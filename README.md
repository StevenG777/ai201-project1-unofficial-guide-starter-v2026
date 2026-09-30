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

**3.** For the criterion 4 diagnosis, I asked Claude to look at chunker.py and figure out the actual mechanism behind the `health_center.txt` miss rather than just restating "it has two topics." It named the stage (chunking) and the specific gap: `split_documents` has no check for a topic boundary inside a file. When I floated fixing it by special-casing the filename, Claude pushed back — pointing out my own chunker.py docstring had already rejected that exact approach, and that it wouldn't generalize to a future file with the same problem. I agreed and asked for a generalizable alternative instead.

**4.** I asked Claude to implement the alternative — paragraph splitting merged back together by embedding similarity — as a new function, `semantic_split_documents`, kept separate from `split_documents` rather than replacing it. Before trusting a threshold, I pushed back that the embedding model is a black box to me and could plausibly treat same-topic paraphrased paragraphs as dissimilar, so I asked it to actually measure this instead of guessing a number. It swept the threshold across the corpus and found none that caught `health_center.txt` without also splitting 50+ genuinely single-topic files (`course_biol_160.txt` among them), and it built a concrete example proving the damage was real — `course_biol_160.txt`'s workload sentence, once separated from its title, drops to rank 27 of 158 chunks for a question it should answer. I used that evidence to reject the improvement myself rather than adopt whatever number made the criterion pass.

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
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Each chunk represents one coherent file-level topic | 88 of 88| 87/88 | 87/88 | 87/88 | MISS |
| 5. For all 5 of my test answers, every factual claim must be traceable to the cited source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

### 1. Retrieved chunk contains the answer
> Produced by `run_eval.py::run_once` (retrieval via `store.py::search`, chunks from
> `chunker.py::split_documents`), cutoff 0.6, top-k 5, 3 runs per question, caching off.
> Full per-run output in `results/run_2026-09-28_2223_before.md`.

### 2. Every answer names a source
> Produced by `run_eval.py::run_once`, same run as above. Full output in
> `results/run_2026-09-28_2223_before.md`.

### 5. For all 5 of my test answers, every factual claim must be traceable to the cited source
> Produced by `run_eval.py::run_once`, same run as above. Full output in
> `results/run_2026-09-28_2223_before.md`.

#### What is the first step in the grade appeal process — run 1

- Best distance: 0.2798 (passed the gate)
- Sources retrieved: admin_grade_appeals.txt, course_engl_205.txt, course_engl_205_exams.txt, course_stat_150.txt, course_stat_150_exams.txt

```
The first step in a grade appeal is to start with the instructor, and it must be raised within fifteen days of the grade posting (admin_grade_appeals.txt).
```

#### When is the deadline to appeal your grade after grades are posted — run 1

- Best distance: 0.2281 (passed the gate)
- Sources retrieved: admin_add_drop_deadline.txt, admin_grade_appeals.txt, admin_pass_fail_option.txt, admin_withdrawal_deadline.txt, course_stat_150.txt

```
A grade appeal has to be raised within fifteen days of the grade posting. 

Source: admin_grade_appeals.txt
```

#### What happen if you skip the instructor when appealing the grade — run 1

- Best distance: 0.2521 (passed the gate)
- Sources retrieved: admin_add_drop_deadline.txt, admin_grade_appeals.txt, admin_pass_fail_option.txt, admin_withdrawal_deadline.txt, course_stat_150.txt

```
If you skip the instructor step, the appeal is returned, which wastes most of the fifteen days allowed to raise the appeal. 

Source: admin_grade_appeals.txt
```

#### What is the last step in the grade appeal process — run 1

- Best distance: 0.2698 (passed the gate)
- Sources retrieved: admin_grade_appeals.txt, course_engl_205.txt, course_engl_205_exams.txt, course_stat_150.txt, course_stat_150_exams.txt

```
Based on the provided documents, a grade appeal starts with the instructor and then goes to the department (admin_grade_appeals.txt). The documents do not mention any further steps beyond going to the department.
```

#### When is the earliest time you can declare your major — run 1

- Best distance: 0.2422 (passed the gate)
- Sources retrieved: admin_add_drop_deadline.txt, admin_declaring_a_major.txt, admin_graduation_requirements.txt, admin_pass_fail_option.txt, admin_study_abroad.txt

You declare your major at the end of your second semester (from admin_declaring_a_major.txt).

### 3. Gate stops out-of-corpus questions
> Produced by `run_eval.py::check_out_of_scope`, cutoff 0.6. Refused 5 of 5.

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.825 | refused |
| How do I change the oil in a diesel engine? | 0.934 | refused |
| Who won the 1994 World Cup? | 0.886 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.844 | refused |
| How do I write a for loop in Rust? | 0.896 | refused |

### 4. Each chunk represents one coherent file-level topic

> No code checks this — it's a manual review, judged against the "on-topic" definition from
> How I Used AI (a reader would recognize it as related to the current topic, and any factual
> claim can be pointed to in the source). Chunks produced by `chunker.py::split_documents`.
> Judged 87/88 coherent. Full set reviewed is saved to
> `results/chunks_all_criterion4.txt` (from `python app.py chunks -n 88`).

**The one failure — `health_center.txt#0`:**

```
The health centre

Walk-in hours are 8am to 11am; everything after that is by appointment and appointments run about a week out. If something is urgent, go at 8am and wait rather than booking.

Counselling is separate, in the same building, and has its own intake process with a shorter wait than people expect — usually three or four days for a first session.
```

The second paragraph (counselling) is a separate topic from the first (urgent-care walk-in
hours) — neither is a detail, exception, or consequence of the other, so this chunk fails the
criterion's own test.

**Two passing chunks, for contrast:**

`dining_pellew_dining_hall.txt#0`:

```
Pellew Dining Hall

Second-year here. Wait times: 12 to 18 minutes at peak, and the peak is early — 11:45 to 12:30. The thing worth going for is a dedicated allergen-free station staffed by someone who knows the menu. The thing to know is that the furthest hall from anywhere, next to the athletics centre.

Hours are 7:00am to 8:00pm daily. Costs one meal swipe, or $11.75 cash.
```

`money_textbooks.txt#0`:

```
The library holds one copy of most required texts on two-hour reserve. For courses where the text is used constantly that isn't enough, but for the reading-light courses it's genuinely all you need.

The campus store price-matches, which is not advertised anywhere and you have to ask at the counter with the other listing on your phone.
```

Every sentence in both stays on the file's single named topic (wait times/hours/cost for one
dining hall; reserve copies/price-matching for textbooks) — no second topic label needed.

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | Check that the answer is found in the retrieved chunk |
| 2 | Every answer names a source | MET | Check the text with keyword cited, source; and file name(s) |
| 3 | Gate stops out-of-corpus questions | MET | Check from the run log that the out-of-corpus questions are refused by the gates. |
| 4 | Each chunk represents one coherent file-level topic | MISS | Analyze the main topic for each corpus, any other topic that are related to the main topic is considered as part of the main topic. A topic that's semantically different and not related in any way is considered a completely separate main topic, while violate the coherence |
| 5 | For all 5 of my test answers, every factual claim must be traceable to the cited source | MET | Extract all factual parts of the answer, and ensure all parts match the main topics fully from the answer to the cited source|

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

### Criterion 4 (chunk coherence) — MISS

**Stage: chunking.**

`chunker.py::split_documents` assumes one file equals one topic and turns every file into a
single chunk with no internal split logic — there's no check for a topic boundary within a
file, so whatever a file contains, coherent or not, becomes one chunk verbatim. That
assumption holds for 87 of 88 files. It breaks for `health_center.txt`, which covers two
unrelated topics in one file: urgent-care walk-in hours in the first paragraph, and a
separate counselling intake process (different hours, different wait time, different
process) in the second. Because `split_documents` never looks for a boundary between them,
both topics end up in `health_center.txt#0` together, and that single chunk fails the "one
coherent topic" test the criterion sets.

**Pattern check.** This is the only chunk of 88 that fails, and `health_center.txt` is the
only file in the corpus that mixes two unrelated topics — every other file was already
written as a single-topic post. So this is one isolated cause, not a systemic chunking
problem: the whole-file strategy is sound for the other 87 files, and rewriting the chunker
to handle "files with two topics" as a general case would be solving a problem that appears
exactly once in the corpus.

**Were my targets set low?** Four of five criteria came in MET on the first pass, which is
the pattern the assignment warns about — safe targets that pass tell you less than targets
that get tested honestly. Criterion 4's target (88/88, zero tolerance) wasn't set with
`health_center.txt` in mind, though — I set 88/88 because my chunking strategy rests on the
one-file-equals-one-topic assumption holding across the whole corpus, and I only found the
exception by actually reviewing all 88 chunks for this unit, not when I wrote the criterion
last unit. So the target did its job: it was strict enough to catch an assumption I hadn't
actually verified yet. The target I'd reconsider instead is criterion 3 (gate stops
out-of-corpus questions, target 4/5) — it came in 5/5 across all three runs with a distance
gap so wide (0.28 best in-corpus vs. 0.83 worst out-of-scope) that nothing in my current test
set is close enough to the boundary to meaningfully stress the gate. Next time I'd tighten it
by adding a harder near-miss question — something adjacent to the corpus but not answerable
from it — rather than keeping five questions worded as unambiguously off-topic as "capital of
Mongolia."

## The Improvement

**What I changed:** Added a second chunker, `chunker.py::semantic_split_documents`, kept
alongside `split_documents` rather than replacing it (selectable with `--chunker` on
`app.py index`/`chunks`, and `--variant` to hold both indexes at once — `default` is the
original, `semantic` is this one). It splits each file into paragraphs, embeds each one, and
merges adjacent paragraphs into one chunk as long as consecutive-paragraph embedding
similarity stays above `config.CHUNK_SIMILARITY_THRESHOLD`; it starts a new chunk when
similarity drops below that. The title line is always glued to the first real paragraph
before any comparison, since a title alone ("The health centre") carries almost no topic
signal on its own.

**Why I picked it:** Directly targets the criterion 4 diagnosis above — `split_documents`
has no mechanism at all for detecting a topic boundary inside a file, so this adds one.

**Calibration — this is where it broke.** Framing it as: *positive* = correctly split
(different topic), *negative* = correctly merge (same topic). I embedded paragraph pairs from
`health_center.txt` (the one real topic-shift case) and from known single-topic multi-paragraph
files (`course_biol_160.txt`, etc.) and swept the threshold:

| Threshold | Catches `health_center.txt`'s real split? | Files wrongly split (false positives) |
|---|---|---|
| 0.15–0.3 | No | 6–41 files |
| ≥ 0.35 | Yes | 54+ files, including `course_biol_160.txt`, `course_stat_150.txt` |

There is no threshold with both decent recall and acceptable precision — the value needed to
catch the one real case also fires on dozens of files that are genuinely single-topic.
Recall and false-positive rate move together here rather than trading off against each other,
which is what it looks like when a feature isn't actually separating the two classes. My best
guess at the mechanism: sentence embeddings encode surface semantic content, not "is this the
same real-world topic as the previous paragraph, allowing for paraphrase." Two paragraphs
about the same dorm can use completely different vocabulary (laundry cost vs. noise) and
embed far apart even though a person would call them the same file's topic, while paragraphs
that share surface vocabulary can embed close together across an actual topic boundary.

I ran the full system anyway at threshold 0.35 (the value needed to fix criterion 4) rather
than abandoning it at the calibration stage, so the after-numbers below are real, not
projected.

### Run Log — After

Produced by `run_eval.py::main`, index variant `semantic` (158 chunks vs. 88 before). Full
per-run output: `results/run_2026-09-29_1959_after.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Each chunk represents one coherent file-level topic | 88 of 88 | 88/88 | 88/88 | 88/88 | MET |
| 5. Every factual claim traceable to the cited source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

Criterion 4 flips from MISS to MET — `health_center.txt` now splits into
`health_center.txt#0` (walk-in hours) and `health_center.txt#1` (counselling), each a single
coherent topic. Criteria 1/2/3/5 stayed MET, unchanged, on my original five test questions.

**But that's misleading, not reassuring — the concrete failure the calibration predicted is
real, it just doesn't happen to touch my five test questions.** `course_biol_160.txt` splits
into three chunks under this chunker: `#0` (course format/assessment, keeps the title "BIOL
160 Cell Biology"), `#1` ("Expect 9 to 11 hours a week, the heaviest first-year course by
reputation." — no course name anywhere in it), `#2` (advice). I asked "How many hours a week
should I expect to spend on BIOL 160?" against both indexes:

```
before (variant=default): distance 0.306, top-5 includes course_biol_160.txt
  "You should expect to spend 9 to 11 hours a week on BIOL 160
  (from course_biol_160_workload.txt and course_biol_160.txt)."

after (variant=semantic): course_biol_160.txt#1 — the chunk with the actual answer —
  ranks 27th of 158 chunks, distance 0.675 (above the 0.6 gate cutoff on its own).
  It never appears in top-5 or top-20.
```

The answer still came out right here, purely because a second file
(`course_biol_160_workload.txt`) happens to state the same fact independently — the corpus
has redundant coverage for hours-per-week questions specifically. Strip that redundancy and
this chunker would make the gate refuse a question the corpus can actually answer, or force
the model to answer from a chunk that no longer says which course it's about. That's the
concrete version of the false-positive-rate problem above: fragmenting a coherent chunk can
delete the very context (a course name, a file's title) that made it retrievable in the
first place.

**Did it help?** For the one thing it targeted — criterion 4 — yes, on paper: 87/88 → 88/88.
But I don't think it's a net improvement, and I'm not adopting it. It fixes one known file by
introducing a mechanism that measurably breaks other, unrelated files (`course_biol_160.txt`
is not an edge case the way `health_center.txt` is — it's an ordinary file that got damaged as
a side effect). My existing five test questions don't happen to expose that damage because of
redundant information elsewhere in the corpus.  I'm keeping `split_documents` (the "before" chunker) as the system's actual
chunker and leaving `semantic_split_documents` in the repo as a documented, measured, rejected
attempt.

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

**Criterion 4 (chunk coherence, 87/88) — still MISS in the deployed system.** I built and
measured an improvement (`semantic_split_documents`), but rejected it after showing it
degrades an unrelated file (`course_biol_160.txt` becomes unretrievable for its own workload
question) worse than the one file it fixes. The system today still runs `split_documents`, so
`health_center.txt` remains one chunk mixing urgent-care hours and counselling.

What I'd try next: a narrower, rule-based split for the specific "two topics in one file"
pattern instead of a generic similarity threshold — detect an explicit topic-shift phrase
("is separate," "also worth saying") and split there, leaving every other file's chunking
untouched. I'd validate it the same way I validated the failure: run it against every
multi-paragraph file in the corpus before trusting it, not just `health_center.txt`. I stopped
here because Milestone 4's budget was already spent building and honestly evaluating the
semantic-merge attempt.

Also worth flagging even though it isn't a miss: criterion 3's target (4 of 5) has never been
meaningfully stress-tested. My five out-of-scope questions sit at distance 0.79–0.93 against a
0.28 worst in-corpus case — nothing close enough to the 0.6 cutoff to tell me whether the gate
would actually catch a harder near-miss question. That's a gap in my test set, not evidence
the gate works well; criterion 3's MET verdict is weaker than the clean 5/5 makes it look.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

**Criterion 4.** I'd keep the target at 88/88 — it did its job, catching an assumption
(one-file-equals-one-topic) I hadn't actually verified when I wrote it. What I'd change is my
own process, not the criterion: I'd read all 88 files for exceptions *before* setting the
target, the way I eventually did during this unit's Milestone 1, rather than setting the
target first and discovering the exception during testing. Same number, entered this unit
already knowing where my one miss was instead of finding it during the test run.

**Criterion 3.** I'd tighten the out-of-scope question set, not the 4-of-5 target. Five
questions that are all as unambiguously off-topic as "capital of Mongolia" don't stress the
gate — I'd add at least one deliberately hard near-miss (plausible-sounding, campus-adjacent,
but not actually in the corpus) so a MET verdict here means something closer to "the gate
caught a genuinely hard case" instead of "the gate caught five easy ones."