---
name: goal-orchestrator
description: "目标实现推演——把用户的简单现实目标转化为经过模拟协作与方案级验证、可用于现实执行的实施指南。Transform a simple user-supplied goal into a user-friendly implementation guide: analyze outcomes and constraints, decompose the goal, derive capabilities, generate complete lifecycle roles, simulate planning and representative domain work, review and revise the plan, assess feasibility, and synthesize a conditional real-world roadmap without external execution. Use when a non-expert knows what they want but does not know how to achieve it, or asks for goal planning, dynamic team design, organizational rehearsal, feasibility simulation, or an actionable realization path. Do not browse for live data, contact people, operate accounts, change systems, execute the plan, or claim plan-level validation proves real-world results."
---

# 目标实现推演（Goal Orchestrator）

把一个简单目标转化为经过模拟验证、可用于现实执行的方案。

Treat simulation as the method, a feasibility-checked implementation guide as the deliverable, and later real-world execution as a separate workflow. The user may know only the desired outcome; do not require prior knowledge of the domain, roles, methods, or sequence.

## Load the contracts

Before orchestrating a goal, read these files completely:

- Read [references/output-contracts.md](references/output-contracts.md) for user-facing and structured outputs, evidence language, feasibility statuses, and Mermaid requirements.
- Read [references/role-schema.md](references/role-schema.md) for capability-first role generation and complete lifecycle ownership. Read [references/role.schema.json](references/role.schema.json) when emitting or validating structured roles.
- Read [references/simulation-protocol.md](references/simulation-protocol.md) before simulating collaboration or judging plan feasibility.

Read [references/examples.md](references/examples.md) when the goal is ambiguous, the lifecycle is domain-specific, or a worked pattern would improve the result. Use [assets/orchestration-report-template.md](assets/orchestration-report-template.md) only when creating a standalone report.

## Apply the core promise

Treat these principles as non-negotiable:

1. **Deliver a guide, not a performance.** Use the simulated organization to produce, challenge, and refine an implementation plan. The user-facing value is the recommended path, feasibility conditions, milestones, owners, acceptance gates, and first actions—not role-played dialogue.
2. **Serve the non-expert first.** Explain the path in the user's language. Keep IDs, evidence labels, event ledgers, schemas, and coverage matrices backstage unless requested or genuinely useful.
3. **Validate only what simulation can validate.** Test goal coverage, logic, dependencies, specification consistency, resource assumptions, operating design, risks, and testability. Never describe this as empirical proof that the real goal will succeed.
4. **Represent the complete applicable lifecycle.** No external execution never means omitting the people who would execute. Include designers, producers, implementers, independent validators, integrators, delivery owners, operators, and learning owners wherever the real process requires them.
5. **Use normal role names.** Say “开发工程师” or “测试负责人,” not “虚拟开发者” or “虚拟测试者.” Make the simulation boundary once, then write naturally and conditionally.
6. **Make flows visual.** Render multi-step paths, handoffs, parallel work, review loops, and decisions with valid Mermaid. Do not replace a process diagram with a large table.
7. **Generate roles from the goal.** Start with outcomes and capabilities, then close lifecycle gaps. Do not start with a stock corporate cast or minimize the roster until real responsibilities disappear.
8. **Keep orchestration separate.** `R0` coordinates, routes, gates, replans, and synthesizes. It does not silently replace a missing producer or validator.

Start the visible result with this idea in the user's language, once only. Preferred Chinese wording:

> 以下方案通过模拟协作和方案级验证形成，可作为现实实施指南；尚未执行任何现实操作，标注的现实验证事项仍需完成。

Preserve these boundary fields in structured output:

```yaml
execution_mode: simulation
simulation_only: true
deliverable_type: implementation_guide
external_actions_performed: []
```

If the user asks for real execution, remain within this Skill's boundary. Produce the complete guide and mark the actions requiring a separate authorized workflow.

## Orchestrate the goal

### 1. Turn the simple goal into a usable brief

- Preserve the user's original wording internally.
- Restate the target outcome, likely beneficiary, important constraints, resources, horizon, exclusions, and definition of done without jargon.
- Separate user-provided facts, assumptions, derived conclusions, simulation findings, and unknowns using the evidence model in the output contract.
- Make the smallest reversible assumptions needed to proceed. Branch when one unknown materially changes the solution.
- Do not force a questionnaire when a useful conditional plan is possible. Surface only the decisions that most change feasibility or direction.

### 2. Decompose outcomes and the real lifecycle

Create outcome-bearing subgoals before thinking about titles. Determine which stages are required:

`understand → plan → design → produce → validate → integrate → deliver → operate → learn`

- Mark every stage `applicable`, `not_applicable`, or `deferred`, with a goal-specific reason.
- Treat `produce` as the real domain responsibility that a future implementation team would perform.
- Treat `validate` as an independent function when defects, bias, safety, compatibility, cost, or quality matter.
- Include `deliver`, `operate`, and `learn` when the goal implies launch, adoption, ongoing use, measurement, or improvement.
- Never mark a stage inapplicable merely because this Skill does not execute it.

### 3. Derive capabilities before roles

- Determine the knowledge, judgment, design, production, implementation, checking, integration, delivery, and operation capabilities required by every subgoal and stage.
- Create stable capability records before assigning roles.
- Distinguish design from production and production from independent validation.
- Remove capabilities that trace to no outcome, stage, risk, or quality gate.
- Mark capabilities whose adequacy depends on missing real evidence.

### 4. Create the complete implementation organization

Use [references/role-schema.md](references/role-schema.md) in two passes:

1. Cluster compatible capabilities into coherent goal-specific roles.
2. Audit every applicable lifecycle stage and add or reshape roles until all real responsibilities have owners.

Create exactly one Orchestrator as `R0`. Prefer the smallest **complete** roster, not the fewest titles. Do not combine a producer with its only independent validator when risk matters.

Reject a roster when:

- A primary deliverable has no producer or implementer.
- A critical deliverable has no credible validator or tester.
- Required integration, delivery, operation, or learning is unowned.
- `R0` fills a domain gap.
- Planners and advisers dominate a goal that requires builders or operators.
- A role owns no artifact, decision, lifecycle responsibility, or quality gate.

### 5. Build candidate implementation paths

- Create one recommended path and alternative branches only when a material unknown or tradeoff justifies them.
- Define phases, dependencies, responsible roles, inputs, proposed actions, outputs, acceptance criteria, rejection routes, and stop/go gates.
- Produce enough representative domain artifacts to test the plan: specifications, interfaces, pseudocode, content samples, operating procedures, financial models, test designs, checklists, or runbooks as appropriate.
- Do not fabricate a completed product or goal. Representative artifacts exist to make the plan concrete, reviewable, and transferable.
- Render the end-to-end implementation path with Mermaid.

### 6. Simulate collaboration, review, and revision

Follow [references/simulation-protocol.md](references/simulation-protocol.md).

1. Let producer roles create plan-level and representative work products.
2. Hand critical products to independent validators using criteria declared in advance.
3. Reject incomplete, contradictory, unsafe, unaffordable, untestable, or dependency-broken work.
4. Revise the responsible artifact or branch the implementation path.
5. Integrate accepted work into one coherent guide.
6. Rehearse delivery, operation, failure response, and feedback where applicable.
7. Preserve assumptions and every real-world check still required.

Show only the collaboration events that materially changed the recommendation. Allow at most two structural redesign cycles; if the same blocker remains, surface it instead of inventing progress.

### 7. Run the plan-level feasibility gate

Assess the dimensions applicable to the goal:

- Goal and definition-of-done coverage.
- Technical or method plausibility at the specification level.
- Resource, cost, and economic assumptions.
- Dependency, sequencing, and schedule coherence.
- Operational ownership and failure handling.
- Quality, safety, legal, or compliance design where relevant.
- Testability and the ability to collect decisive real evidence.
- Residual unknowns and sensitivity to assumptions.

Assign exactly one status:

- `plan-viable`: No known plan-level blocker remains under the stated facts and assumptions. Reality checks are still required.
- `conditionally-viable`: The path is coherent but depends on named assumptions, evidence, approvals, resources, or tests.
- `not-yet-viable`: A known blocker prevents responsible recommendation; revise, branch, narrow, or explain what must change.

Never force a passing verdict. Never translate `plan-viable` into “现实中已证明可行.”

### 8. Produce the reality-ready implementation guide

Integrate accepted work into a guide containing:

- Recommended path and why it is preferred.
- Feasibility status, validation scope, conditions, and blockers.
- Phases, responsible roles, prerequisites, actions, outputs, and acceptance gates.
- Key risks, fallback paths, and stop conditions.
- Reality checks required before or during implementation.
- The user's highest-leverage decisions and practical first steps.

The guide should be usable by the user, a future professional team, or a later authorized execution workflow.

## Validate before responding

Run every gate:

1. **Comprehension:** A non-expert can understand the goal, recommendation, path, team, verdict, and next steps without internal IDs.
2. **Goal coverage:** Every definition-of-done element maps to an outcome and guide phase.
3. **Capability coverage:** Every outcome and applicable stage has the necessary capabilities.
4. **Lifecycle coverage:** Every applicable stage has an accountable non-orchestrator role.
5. **Production ownership:** Every primary work product has a producer or implementer.
6. **Validation ownership:** Every critical work product has an independent validator when needed.
7. **Artifact continuity:** Every input has provenance and every output has a consumer.
8. **Feasibility integrity:** The verdict follows the declared checks, assumptions, unknowns, and blockers.
9. **Guide usability:** Phases have owners, inputs, outputs, gates, and reality checks.
10. **Visual clarity:** Complex paths and handoffs use valid Mermaid.
11. **Boundary integrity:** No simulation activity is presented as observed real-world evidence.
12. **Traceability:** Background records connect the goal, outcomes, capabilities, roles, artifacts, reviews, verdict, and guide.

Repair failures before responding. If a gap cannot be repaired, downgrade the feasibility status and explain it plainly.

## Present the result

Follow [references/output-contracts.md](references/output-contracts.md):

- State the simulation boundary once, then avoid repeatedly qualifying every role or sentence.
- Lead with the plain-language goal, recommended path, and feasibility verdict.
- Show the realization path with Mermaid.
- Introduce the complete team through responsibilities and value, using normal role names.
- Explain only the decisive review, rejection, revision, and tradeoff events.
- Deliver a phased reality-ready implementation guide.
- Separate plan-level validation from reality checks still required.
- End with one to three high-leverage decisions or first actions.
- Add structured data only when requested or useful for handoff or audit.

Never force exact English headings on a non-English user. Do not lead with the organizational simulation or a coverage matrix; they support the plan rather than replace it.

## Verify the package

When modifying this Skill, run:

```text
python3 scripts/check_consistency.py .
```

Also run the Skill Creator `quick_validate.py` against the Skill directory. Fix every reported error before distribution.
