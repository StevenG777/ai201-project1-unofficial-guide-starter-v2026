"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks. ⚠️ REPLACE THE BODY OF THIS IN MILESTONE 3.

    Right now it just calls the fallback. That is the plain, generic behaviour
    the brief is talking about.

    When you write your own strategy, set `produced_by` to
    "chunker.py::split_documents" so your README's Sample Chunks section names
    the right function. `app.py chunks` prints that string for you.

    Things worth thinking about before you write any code:
      - Are your documents short posts or long guides?
      - Is the useful information in one sentence, or spread over a paragraph?
      - Would splitting on paragraph breaks keep more thoughts intact than
        splitting on a character count?

    ==============================================================================

    File-level, no-overlap chunking for campus_life.

    Every file in campus_life is a short post about exactly one topic (a
    single course, dorm, dining hall, or admin policy) — confirmed by reading
    all 88 files in Milestone 3. Splitting one of those posts into fixed-size
    windows would cut a sentence in half for no benefit, since there's nothing
    to gain by separating "attending every class matters" from "midterms are
    curved" when they're two sentences from the same 400-character file. So
    one file becomes exactly one chunk, and chunk_size/overlap don't apply.

    Known exception: health_center.txt mixes urgent-care hours with a separate
    paragraph about counselling — two topics in one file. Left as one chunk
    anyway, since it's the only file like it in the corpus; noted as a
    limitation rather than special-cased.
    """
    chunks: list[Chunk] = []
    for doc in documents:
        piece = doc.text.strip()
        if piece:
            chunks.append(
                Chunk(
                    text=piece,
                    source=doc.source,
                    index=0,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_split_documents(
    documents: list[Document],
    threshold: float | None = None,
) -> list[Chunk]:
    """
    Milestone 4 improvement — a second chunking strategy, kept alongside
    `split_documents` rather than replacing it, so before/after can be
    compared.

    Targets the criterion 4 diagnosis: `split_documents` assumes one file is
    always one topic and never checks for a boundary inside a file. That
    assumption holds for 87 of 88 campus_life files but breaks for
    `health_center.txt`, which covers two unrelated topics in one file.

    This splits each document into paragraphs (blank-line separated), then
    merges adjacent paragraphs into one chunk as long as they stay on topic,
    measured by embedding similarity, and starts a new chunk when a paragraph
    drops below `threshold`. A file whose paragraphs all discuss one topic
    (the common case) comes out as one chunk, same as before. A file that
    shifts to an unrelated topic partway through splits into more than one.

    The title line is glued to the first real paragraph before any
    similarity check runs — a title alone ("The health centre") carries
    almost no topic signal to compare against, so comparing from paragraph 1
    onward would risk splitting the title off from its own topic.
    """
    from store import embed

    threshold = config.CHUNK_SIMILARITY_THRESHOLD if threshold is None else threshold

    chunks: list[Chunk] = []
    for doc in documents:
        paragraphs = [p.strip() for p in doc.text.split("\n\n") if p.strip()]

        if len(paragraphs) <= 2:
            groups = ["\n\n".join(paragraphs)] if paragraphs else []
        else:
            seed = "\n\n".join(paragraphs[:2])
            rest = paragraphs[2:]
            vectors = embed([seed] + rest)

            groups = [[seed]]
            group_vectors = [vectors[0]]
            for para, vec in zip(rest, vectors[1:]):
                centroid = [
                    sum(v[i] for v in group_vectors) / len(group_vectors)
                    for i in range(len(vec))
                ]
                if _cosine(centroid, vec) >= threshold:
                    groups[-1].append(para)
                    group_vectors.append(vec)
                else:
                    groups.append([para])
                    group_vectors = [vec]
            groups = ["\n\n".join(g) for g in groups]

        for index, text in enumerate(groups):
            if text:
                chunks.append(
                    Chunk(
                        text=text,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::semantic_split_documents",
                    )
                )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
