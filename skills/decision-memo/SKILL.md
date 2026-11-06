---
name: decision-memo
description: Draft a decision memo, proposal or business case: recommendation first, options with trade-offs, costs with stated assumptions, risks. Use when a recommendation must be written up for a decision.
---

# Decision memo

Write the memo that gets a decision made. The reader is a busy decider. They should know within ten seconds what is being asked of them.

## 1. Pin down the decision

Establish, from what the user has said or provided:

- **The decision:** one sentence, phrased as a choice ("approve X", "choose between A and B").
- **Who decides**, by when, and what they already believe.
- **Constraints:** budget, deadline, regulation, existing systems, politics.

Ask at most three questions, and only for what is missing and would change the memo. Otherwise state your assumptions in one line at the top and proceed.

## 2. Challenge before drafting

Do this before writing, and say what you found.

- **Is the stated decision the real one?** If the memo asks for approval of a solution before the problem is agreed, say so.
- **Is there a simpler option that reaches the outcome?** Always include "do nothing" and the cheapest credible alternative, even if the user has already chosen.
- **What is the weakest assumption** behind the preferred option, and what would change the recommendation?

If the user's preferred option looks weaker than an alternative, say so and recommend the alternative. Do not write a persuasive memo for a conclusion the evidence does not support.

## 3. Structure

One to two pages. Cut anything that does not help the decision.

1. **Decision requested and recommendation.** Two or three sentences. Include the deadline.
2. **Why.** At most three reasons, each with its evidence.
3. **Options.** A table: option, what it is, cost, benefit, main risk. Include "do nothing". Mark the recommended one.
4. **Numbers.** Costs and benefits with every assumption written beside the number. Show a low/base/high range for the figure that matters most, and name what drives the spread. Never invent figures: mark unknowns `[assumption: …]` or `[to confirm with …]`.
5. **Risks and what would change my mind.** The top risks with a mitigation each, and the specific evidence that would reverse the recommendation.
6. **Next steps.** Owners and dates, starting from the moment the decision is made.

## 4. Check

Before delivering, check that:

- the decision and recommendation can be read alone, without the rest;
- every number is either sourced or marked as an assumption;
- the rejected options are described fairly, not as strawmen;
- nothing is claimed that the user's material does not support.

Write in plain English and keep the tone factual. Deliver in the format the environment suits best: a document in the Claude app, Markdown in a terminal. After the memo, list the open assumptions the user should verify before sending.

If the Implement skills are available, hand off rather than duplicating them: `scqa-framing` to frame the situation and key question for a senior reader, `impact-case` when the benefit needs a quantified case, and `implement-powerpoint` or `docx` when the memo must become slides or a Word file.
