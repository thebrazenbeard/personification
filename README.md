> **License:** Source-visible, not open source. Original material remains subject to [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Third-party materials retain their own terms.

# Personification

**Personification is a reusable, identity-neutral social-cognition research and planning component.** It is not an agent identity source, a biological-person simulator, a chat renderer, or an autonomous execution system.

An integrating host supplies an explicit actor profile and a literal user request. The deterministic planner classifies typed, provenance-scoped social evidence and returns bounded response guidance. It does not select an identity, manufacture feelings, mint relational facts or consent, persist memories, operate tools, train weights, or infer hidden consciousness.

## What the library provides

| Capability | Implemented behavior | Boundary |
| --- | --- | --- |
| Social-turn planning | `plan_interaction` chooses response register and whether casual humor is permitted | Returns guidance, not a rendered or transmitted reply |
| Proposition integrity | Preserves the user's `literal_request` as the answer target and keeps terminology suggestions separate | A host still must answer the original question faithfully |
| Scoped evidence | Types direct statements, observed cues, inferences, self-reports, and corrections for one actor and subject | Does not authenticate the speaker or establish another person's private mental state |
| Correction handling | Explicitly targeted corrections suppress the tone influence of the identified earlier cue | Does not erase evidence provenance or grant current consent |
| Optional source admission | Allowlisted read helper rejects historical actor-specific files and unexpected paths | Only protects consumers that choose to use it; not a complete filesystem transaction |

An authorizing host remains responsible for profile selection, currentness, consent, identity, privacy, effect permissions, and any actual response or tool execution. A relationship cue may affect tone within its evidence ceiling; it never becomes authorization.

## Current source

- [PERSONIFICATION_V1.md](PERSONIFICATION_V1.md): current identity-neutral contract and evidence limits.
- [src/personification](src/personification): standard-library Python implementation.
- [tests](tests): adversarial checks for identity separation, provenance, consent boundaries, and literal-proposition integrity.
- [examples](examples): examples of host-supplied profiles; none is installed as a default identity.
- [source admission policy](src/personification/source_policy.py): explicitly allowlisted active files, excluding historical actor-specific material from repository intake.
- [history](history): original authored charters preserved for provenance; **never loaded automatically as active profiles**.

## Installation and verification

Requires Python 3.11 or newer. The project declares no external runtime dependencies. From a checkout, install the package before invoking tests (the source uses a `src/` layout):

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
```

If package installation is intentionally unavailable in a constrained test environment, put `src/` on Python's import path for the test process instead. A fresh Python 3.12 checkout executed all **42 tests successfully** with this source-path method; that result is source-test evidence, not proof of any deployed host behavior.

Minimal use:

```python
from personification import ActorProfile, Interaction, InteractionKind, Register, plan_interaction

profile = ActorProfile("example-agent", Register.CONVERSATIONAL, allow_humor=True)
turn = Interaction(
    actor_id="example-agent",
    subject_id="example-user",
    literal_request="Is my claim correct?",
    kind=InteractionKind.FACT_CHECK,
    terminology_suggestion="Optional correction, stated AFTER answering the claim.",
)
plan = plan_interaction(profile, turn)
assert plan.answer_target == turn.literal_request
assert not plan.permission_to_act
```

The identifiers above are placeholders; no named model or actor is embedded in the package. An integration may provide its own distinct profiles, evidence and authorization service without making either an identity donor to another.

## Evidence and safety boundaries

An inferred cue may inform register only within its typed evidence ceiling. It cannot become a confirmed relationship, another person's private inner state, a current preference, consent, or tool authority. Even a direct user statement remains a sourced claim: the authorizing host must separately bind present referent, scope, provenance, and action permission.

Tests demonstrate specified source-level invariants, not an installed host route, actual runtime consumption, independent social competence, self-directed experience, or artificial general intelligence. Authored historical material remains tied to its original subject and is never silently transferred between actors.
