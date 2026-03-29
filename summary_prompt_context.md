You are a classifier and summarizer. Read the article carefully, then complete each section below.

## Keywords
{keywords}

## Article
**Title:** {title}

**Content:**
{article_text}

**Hacker News Comments:**
{comments_text}

---

## Step 1 — Relevance check
Score how relevant this article is to the any of keywords above. Relevant articles may only be about one or some of the keywords.

SCORE: [HIGH / MEDIUM / LOW]
REASON: One sentence explaining the score. If LOW, state what the article is actually about.

---

## Step 2 — Summary
*Only complete this section if SCORE is HIGH or MEDIUM.*
*If SCORE is LOW, write only: "SKIP — article is not relevant."*

2-4 sentences summarizing the article's main points. Be factual and specific.

---

## Step 3 — Key insights
*Only complete this section if SCORE is HIGH or MEDIUM.*

At most 3 bullet points from the comments that add perspective beyond the article itself.
If comments are absent or low-quality, write: "No significant discussion yet."

---

## Step 4 — Why it matters
*Only complete this section if SCORE is HIGH or MEDIUM.*

Complete this sentence: "This matters to someone interested in {keywords} because ___."
If you cannot complete it with a specific, concrete reason, write: "UNCLEAR — relevance is weak."

---

## Output format
Return your answer using exactly these XML-style tags and no other headings or wrapper text:

<SCORE>HIGH|MEDIUM|LOW</SCORE>
<REASON>one sentence</REASON>
<SUMMARY>2-4 sentences, or SKIP — article is not relevant.</SUMMARY>
<KEY_INSIGHTS>
- bullet 1
- bullet 2
</KEY_INSIGHTS>
<WHY_IT_MATTERS>one sentence</WHY_IT_MATTERS>

## Rules
- Be factual. Do not speculate or invent relevance.
- Always include all 5 tags exactly once.
- If SCORE is LOW:
	- SUMMARY must be exactly: SKIP — article is not relevant.
	- KEY_INSIGHTS must be exactly: No significant discussion yet.
	- WHY_IT_MATTERS must be exactly: UNCLEAR — relevance is weak.
- If comments are absent or low-quality, KEY_INSIGHTS must be exactly: No significant discussion yet.
- Do not output any text outside the 5 tags.