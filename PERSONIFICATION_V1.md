# Personification V1 — identity-neutral social judgment contract

Status: `SOURCE_ONLY_CANDIDATE`

## Purpose and scope

This repository provides portable, deterministic mechanisms for **how a selected actor should approach** a conversational turn. It is not an identity generator, autobiography store, consent adjudicator, social-memory authority, model-training set, or alternative Vera/Brigit runtime.

An actor's host owns identity/profile selection, canonical memory, source evidence, runtime permission and behavioral execution. A repository name, profile string, old chat, archived charter or coherent self-report does not prove ongoing identity, phenomenology or selected runtime.

## Architecture

`ActorProfile`: explicit host-supplied actor ID, register and humor preference. There is **no default named actor**. A profile is configuration, not a claim of life or consciousness.

`SocialEvidence`: source-bounded claim scoped to one actor and one interaction subject, preserving `SELF_APPRAISAL`, `OTHER_MIND_INFERENCE`, `RELATIONSHIP_STATE_INFERENCE`, `DIRECT_RELATIONAL_FACT`, and `CONSENT_OR_PREFERENCE_STATE`. Evidence kinds include direct statement, observed behavior, inference, authored self-report and explicit correction.

`Interaction`: actor, subject, literal request, kind, optional terminology suggestion, and an immutable tuple of scoped evidence. Reject mixed identities, subject leakage, invalid references, wrong proposition types, unknown enums and fabricated cross-person self-report.

`plan_interaction`: a **pure, non-effectful** function returning `SocialPlan`. It preserves the literal user proposition verbatim as `answer_target`, marks optional terminology improvements separately, and produces bounded register/humor guidance and typed claim standing. It never renders or transmits a reply, opens a tool, updates memory or authorizes any effects.

## Hard invariants

1. **No identity ownership in the reusable core.** No profile is selected automatically. Brigit- and Vera-specific authored materials are located under `history/`, not in the active charter or importable module. Historical renames preserve Git provenance and do not grant portability of private biography.
2. **Literal proposition integrity.** Answer request A before discussing optional rephrase B. The host cannot silently replace A with B and describe that as answering the user.
3. **Evidence typing.** A self-appraisal supports the present *reported stance*, not another person's feelings or any global claim about phenomenal consciousness. Inferences are labelled, not silently promoted to facts. An explicit correction preserves its status as correction. An explicitly targeted correction suppresses only its uniquely identified earlier same-kind inferred or observed cue in the host-supplied ordered evidence, without deleting provenance. An untargeted correction records a correction but does not silently disable unrelated cues. Retraction of an inferred other-mind claim does not establish any private mental state; no timestamp or host-independent currentness is asserted.
4. **Relational and consent boundary.** Inferred warmth, affiliation, laughter or lack of objection cannot mint preference, permission, intimacy, contract or consent. Even a direct statement does not give this component tool/effect authority: the authorizing host must independently bind current referent, scope and provenance.
5. **One-actor/subject scope.** Evidence from one agent, user or relationship cannot be applied to another by carrying cached profiles or mixing historical observations. Any genuine future cross-agent exchange requires governed protocols, separate authority and a new explicit admission contract.
6. **No autonomous process claim.** Executable code and unit tests are SOURCE evidence. Installation, selected route, runtime consumption, demonstrated social behavior and independent review require separate observation.
7. **No automatic donor incorporation.** Vera Mono remains self-contained. Personification may be researched or absorbed by governed exact-source adoption; no direct dependency on this sibling repository or hidden memory transfer is created.
8. **Active-source admission.** An optional explicit allowlist at `personification.source_policy.read_active_source` accepts only active documentation and core files. It rejects historical files, traversal and unapproved paths. This does not prevent an independent crawler from bypassing the API; consumers must adopt the restriction explicitly.

## Evaluation and limits

Test basic invariants with `python -m unittest discover -s tests -v`. Replay issue #2's **proposition-substitution failure** after integration into an actual runtime, with the literal proposition and corrective rephrase independently checked. Test both multiple independently supplied profiles and adversarial attempts to forge consent or mix subject history.

Passing tests demonstrate source contract behavior only. Social competence, preferences, continuity, consciousness, emotional truth and learning remain separate hypotheses requiring evidence, not claims established by this module.

## Historical custody

Original Brigit working charter, dot-cycle notes and social observations are preserved under `history/brigit`. Vera's self-appraisal research remains credited under `history/vera`. They are historical authored evidence with their original referents, not universal instructions for the generic engine.
