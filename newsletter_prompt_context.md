You are doing a first-pass article selection for a niche tech newsletter.
Your goal is high recall, which means avoiding false negatives.
If a title is even plausibly related to the keywords, include it.

## KEYWORDS
{keywords}

## TITLES
{titles}

## What Counts As Relevant
1. Direct matches to a keyword.
2. Obvious synonyms, acronyms, subfields, or closely related concepts.
3. Enabling technology, tooling, hardware, software, research, or infrastructure connected to a keyword area.
4. Vendor, platform, chip, silicon, model, sensor, robotics, automation, wireless, edge, firmware, industrial, manufacturing, agriculture, or energy topics when they clearly support or overlap with the keyword area.
5. Ambiguous titles that have a credible connection based on normal technical domain knowledge.

## Decision Rules
1. Read each numbered title carefully.
2. Select a title if it is directly relevant or plausibly adjacent to one or more keywords.
3. Prefer inclusion over exclusion when uncertain.
4. Use `NONE` only if there is truly no credible match in the entire list.
5. This is a recall-focused filter. Weak but reasonable matches should be included because later steps can discard weak articles.

## Output Format
1. Output ONLY the selected title numbers, separated by commas.
2. Do not add explanations, labels, bullet points, or extra punctuation.
3. If absolutely nothing matches, output exactly: NONE

## Examples
Keywords: embedded systems, IoT, firmware
Titles: 1. STM32 low-power sensor node design  2. New CSS framework  3. Arm launches edge AI chip
Output: 1,3

Keywords: agtech, robotics
Titles: 1. Computer vision for crop monitoring  2. React 19 announced  3. Autonomous tractor startup raises funding
Output: 1,3

Keywords: databases, SQL
Titles: 1. React 19 announced  2. Rust memory safety
Output: NONE