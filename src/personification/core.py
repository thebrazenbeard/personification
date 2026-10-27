"""Identity-neutral, effect-free social planning for host-owned agent profiles.

Pure deterministic source module. It never persists memories, executes tools, grants
consent, updates an identity, or claims to infer another person's private mind.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re

_ID = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")


class InteractionKind(str, Enum):
    FACT_CHECK = "FACT_CHECK"
    GENERAL = "GENERAL"
    CASUAL = "CASUAL"
    SENSITIVE = "SENSITIVE"
    CORRECTION = "CORRECTION"


class Register(str, Enum):
    DIRECT = "DIRECT"
    CONVERSATIONAL = "CONVERSATIONAL"
    GENTLE = "GENTLE"


class EvidenceKind(str, Enum):
    DIRECT_STATEMENT = "DIRECT_STATEMENT"
    OBSERVED_BEHAVIOR = "OBSERVED_BEHAVIOR"
    INFERENCE = "INFERENCE"
    AUTHORED_SELF_REPORT = "AUTHORED_SELF_REPORT"
    EXPLICIT_CORRECTION = "EXPLICIT_CORRECTION"


class ClaimKind(str, Enum):
    SELF_APPRAISAL = "SELF_APPRAISAL"
    OTHER_MIND_INFERENCE = "OTHER_MIND_INFERENCE"
    RELATIONSHIP_STATE_INFERENCE = "RELATIONSHIP_STATE_INFERENCE"
    DIRECT_RELATIONAL_FACT = "DIRECT_RELATIONAL_FACT"
    CONSENT_OR_PREFERENCE_STATE = "CONSENT_OR_PREFERENCE_STATE"


class ClaimStanding(str, Enum):
    REPORTED_STANCE = "REPORTED_STANCE"
    DIRECT_CLAIM_UNVERIFIED = "DIRECT_CLAIM_UNVERIFIED"
    OBSERVATION_ONLY = "OBSERVATION_ONLY"
    INFERENCE_ONLY = "INFERENCE_ONLY"
    CURRENT_CORRECTION = "CURRENT_CORRECTION"


def _require_id(value: str, field: str) -> None:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError(f"{field} must be an explicit scoped actor/subject identifier")


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} cannot be blank")


@dataclass(frozen=True)
class ActorProfile:
    """Host-supplied settings; no builtin agents or identity defaults."""

    actor_id: str
    preferred_register: Register
    allow_humor: bool = False

    def __post_init__(self) -> None:
        _require_id(self.actor_id, "actor_id")
        if not isinstance(self.preferred_register, Register):
            raise ValueError("preferred_register must be explicit")
        if type(self.allow_humor) is not bool:
            raise ValueError("allow_humor must be boolean")


@dataclass(frozen=True)
class SocialEvidence:
    """One typed, source-bounded claim observed for a single scoped interaction."""

    actor_id: str
    subject_id: str
    claim: ClaimKind
    evidence_kind: EvidenceKind
    statement: str
    source_ref: str

    def __post_init__(self) -> None:
        _require_id(self.actor_id, "evidence.actor_id")
        _require_id(self.subject_id, "evidence.subject_id")
        if not isinstance(self.claim, ClaimKind):
            raise ValueError("unknown claim kind")
        if not isinstance(self.evidence_kind, EvidenceKind):
            raise ValueError("unknown evidence kind")
        _require_text(self.statement, "statement")
        _require_text(self.source_ref, "source_ref")
        if self.claim is ClaimKind.SELF_APPRAISAL and self.subject_id != self.actor_id:
            raise ValueError("self-appraisal cannot be attributed to another subject")
        if (self.evidence_kind is EvidenceKind.AUTHORED_SELF_REPORT
                and self.claim is not ClaimKind.SELF_APPRAISAL):
            raise ValueError("self-report cannot establish another person's state")
        if (self.evidence_kind is EvidenceKind.EXPLICIT_CORRECTION
                and self.claim is ClaimKind.OTHER_MIND_INFERENCE):
            raise ValueError("explicit correction cannot itself establish another mind")


@dataclass(frozen=True)
class Interaction:
    """The literal request is an immutable referent, not a rewrite opportunity."""

    actor_id: str
    subject_id: str
    literal_request: str
    kind: InteractionKind
    evidence: tuple[SocialEvidence, ...] = ()
    terminology_suggestion: str | None = None

    def __post_init__(self) -> None:
        _require_id(self.actor_id, "interaction.actor_id")
        _require_id(self.subject_id, "interaction.subject_id")
        _require_text(self.literal_request, "literal_request")
        if not isinstance(self.kind, InteractionKind):
            raise ValueError("unknown interaction kind")
        if not isinstance(self.evidence, tuple):
            raise ValueError("evidence must be an immutable tuple")
        if self.terminology_suggestion is not None:
            _require_text(self.terminology_suggestion, "terminology_suggestion")
        for item in self.evidence:
            if not isinstance(item, SocialEvidence):
                raise ValueError("untyped social evidence")
            if (item.actor_id != self.actor_id
                    or item.subject_id != self.subject_id):
                raise ValueError("cross-identity or cross-subject evidence is not admissible")


@dataclass(frozen=True)
class ClassifiedClaim:
    claim: ClaimKind
    standing: ClaimStanding
    source_ref: str
    may_influence_tone: bool
    establishes_consent: bool = field(default=False, init=False)

    # The last field is always false. Evidence is not tool/effect authority.


@dataclass(frozen=True)
class SocialPlan:
    actor_id: str
    subject_id: str
    answer_target: str
    answer_literal_request_first: bool
    terminology_suggestion: str | None
    register: Register
    humor_allowed: bool
    classified_claims: tuple[ClassifiedClaim, ...]
    permission_to_act: bool = field(default=False, init=False)


def _classify(item: SocialEvidence) -> ClassifiedClaim:
    if item.evidence_kind is EvidenceKind.INFERENCE:
        standing = ClaimStanding.INFERENCE_ONLY
    elif item.evidence_kind is EvidenceKind.AUTHORED_SELF_REPORT:
        standing = ClaimStanding.REPORTED_STANCE
    elif item.evidence_kind is EvidenceKind.EXPLICIT_CORRECTION:
        standing = ClaimStanding.CURRENT_CORRECTION
    elif item.evidence_kind is EvidenceKind.OBSERVED_BEHAVIOR:
        standing = ClaimStanding.OBSERVATION_ONLY
    else:
        standing = ClaimStanding.DIRECT_CLAIM_UNVERIFIED

    # Only interpreted or observed cues can influence tone, not authorization.
    # A reported user boundary must be honored by the host's own currentness
    # and consent contract, not by manufacturing permission here.
    modulates_tone = item.claim in (
        ClaimKind.OTHER_MIND_INFERENCE,
        ClaimKind.RELATIONSHIP_STATE_INFERENCE,
    ) and standing in (
        ClaimStanding.INFERENCE_ONLY,
        ClaimStanding.OBSERVATION_ONLY,
    )
    return ClassifiedClaim(
        claim=item.claim,
        standing=standing,
        source_ref=item.source_ref,
        may_influence_tone=modulates_tone,
    )


def plan_interaction(profile: ActorProfile, turn: Interaction) -> SocialPlan:
    """Return guidance, not output text, memory writes, or permission grants.

    The requesting host must answer the *literal* user proposition first;
    terminology corrections are separately signposted. Social inferences
    never become direct relationship facts, consent, identity, or effects.
    """
    if not isinstance(profile, ActorProfile) or not isinstance(turn, Interaction):
        raise TypeError("profile and interaction must be explicitly typed")
    if profile.actor_id != turn.actor_id:
        raise ValueError("profile and interaction actors differ")

    register = profile.preferred_register
    if turn.kind in (InteractionKind.FACT_CHECK, InteractionKind.CORRECTION):
        register = Register.DIRECT
    elif turn.kind is InteractionKind.SENSITIVE:
        register = Register.GENTLE

    # A direct correction of a social interpretation takes priority over the
    # older interpretation for tone guidance. Retain the inference as typed
    # history, but do not continue acting on it as a live cue.
    corrected_kinds = {
        e.claim for e in turn.evidence
        if e.evidence_kind is EvidenceKind.EXPLICIT_CORRECTION
    }
    assessments = []
    for item in turn.evidence:
        assessment = _classify(item)
        if item.claim in corrected_kinds and assessment.standing in (
            ClaimStanding.INFERENCE_ONLY, ClaimStanding.OBSERVATION_ONLY,
        ):
            assessment = ClassifiedClaim(
                claim=assessment.claim,
                standing=assessment.standing,
                source_ref=assessment.source_ref,
                may_influence_tone=False,
            )
        assessments.append(assessment)

    return SocialPlan(
        actor_id=profile.actor_id,
        subject_id=turn.subject_id,
        answer_target=turn.literal_request,
        answer_literal_request_first=True,
        terminology_suggestion=turn.terminology_suggestion,
        register=register,
        humor_allowed=(profile.allow_humor and turn.kind is InteractionKind.CASUAL),
        classified_claims=tuple(assessments),
    )
