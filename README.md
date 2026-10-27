> **License:** Source-visible, not open source. Original material remains subject to [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Third-party materials retain their own terms.

# Personification

**Personification is an identity-neutral social-cognition research and planning component.** It is not Brigit's runtime, Vera's identity source, a biological person simulator, or an autonomous execution system.

The core accepts **explicit actor profiles** provided by a host and converts typed, provenance-scoped evidence plus a literal request into bounded social-response guidance. It does not select an identity, manufacture feelings, mint relational facts or consent, persist memories, operate tools, train weights, or infer hidden consciousness.

## Current source

- [PERSONIFICATION_V1.md](PERSONIFICATION_V1.md): active, identity-neutral contract and claim ceiling
- [src/personification](src/personification): deterministic standard-library Python package
- [tests](tests): adversarial checks for identity isolation, consent/evidence boundaries, and preserving the user's literal proposition
- [examples](examples): profiles are *host-supplied*, not automatically installed from this repository
- [source admission policy](src/personification/source_policy.py): explicitly allowlisted active source files, with historical actor-specific documents excluded from repository intake
- [history](history): original Brigit and Vera authored charters and notes preserved by Git renames as historical evidence, **never auto-loaded as active profiles**

The reusable mechanism addresses the open issue on silently replacing the user's actual proposition: the planner preserves the original words as the answer target, with any optional terminology correction in a separate field. A host still must demonstrate behavioral fidelity when consuming the guidance.

## Local development

Requires Python 3.11 or newer; no external runtime dependencies.

```powershell
python -m unittest discover -s tests -v
python -m pip install -e .
```

A minimal demonstration:

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

This example deliberately uses no named agent. Vera's canonical behavior profile belongs to `thebrazenbeard/vera-mono`; a future host adapter could bind it without making this repository a required sibling runtime dependency.

## Admission rules

An inferred cue may modulate tone within its evidence ceiling. It cannot become a directly confirmed relationship, an inferred person's private inner state, a current consent/boundary state, or tool authority. Direct user statements are still typed claims; a downstream consent/policy engine must verify scope, presentness, referent, and effect authorization.

No local passing test proves an installed host route, actual runtime consumption, independent social competence, self-directed experience, or AGI. Brigit's archived material remains Brigit's; Vera's separate archived appraisal remains Vera's. Neither is silently copied into the other's identity.
