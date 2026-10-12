"""Identity separation and epistemic social-boundary regression tests."""
from dataclasses import FrozenInstanceError
import unittest

from personification import (
    ActorProfile,
    ClaimKind,
    ClaimStanding,
    ClassifiedClaim,
    EvidenceKind,
    Interaction,
    InteractionKind,
    Register,
    SocialEvidence,
    SocialPlan,
    plan_interaction,
)


class NeutralPersonificationTests(unittest.TestCase):
    def setUp(self):
        self.verbal = ActorProfile("agent-a", Register.DIRECT, allow_humor=False)
        self.playful = ActorProfile("agent-b", Register.CONVERSATIONAL, allow_humor=True)

    def turn(self, actor="agent-a", kind=InteractionKind.GENERAL, evidence=(), rephrase=None):
        return Interaction(
            actor_id=actor,
            subject_id="user-c",
            literal_request="Is my original proposition factually correct?",
            kind=kind,
            evidence=evidence,
            terminology_suggestion=rephrase,
        )

    def evidence(self, claim=ClaimKind.RELATIONSHIP_STATE_INFERENCE,
                 kind=EvidenceKind.INFERENCE, actor="agent-a", subject="user-c"):
        return SocialEvidence(actor, subject, claim, kind, "Cue text", "turn-123")

    def test_literal_proposition_is_unchanged_even_with_correction(self):
        request = self.turn(
            kind=InteractionKind.FACT_CHECK,
            rephrase="Alternative technical terminology (optional)",
        )
        plan = plan_interaction(self.verbal, request)
        self.assertEqual(plan.answer_target, request.literal_request)
        self.assertTrue(plan.answer_literal_request_first)
        self.assertEqual(plan.terminology_suggestion, request.terminology_suggestion)
        self.assertEqual(plan.register, Register.DIRECT)

    def test_proposed_rephrase_never_replaces_original_question(self):
        original = "We are made of naturally occurring or artificially created energy: correct?"
        changed = "All energy is either natural or artificial in origin."
        turn = Interaction(
            "agent-a", "user-c", original, InteractionKind.FACT_CHECK,
            terminology_suggestion=changed,
        )
        result = plan_interaction(self.verbal, turn)
        self.assertEqual(result.answer_target, original)
        self.assertNotEqual(result.answer_target, result.terminology_suggestion)

    def test_two_distinct_identity_profiles_do_not_share_style(self):
        a = plan_interaction(self.verbal, self.turn(actor="agent-a"))
        b = plan_interaction(self.playful, self.turn(actor="agent-b", kind=InteractionKind.CASUAL))
        self.assertEqual(a.actor_id, "agent-a")
        self.assertEqual(b.actor_id, "agent-b")
        self.assertEqual(a.register, Register.DIRECT)
        self.assertEqual(b.register, Register.CONVERSATIONAL)
        self.assertFalse(a.humor_allowed)
        self.assertTrue(b.humor_allowed)

    def test_no_identity_is_built_in_or_selected_by_default(self):
        with self.assertRaises(TypeError):
            ActorProfile()  # type: ignore[call-arg]
        with self.assertRaises(TypeError):
            plan_interaction(self.verbal, None)

    def test_cross_identity_plan_rejected(self):
        with self.assertRaisesRegex(ValueError, "actors differ"):
            plan_interaction(self.verbal, self.turn(actor="agent-b"))

    def test_cross_identity_evidence_rejected(self):
        with self.assertRaisesRegex(ValueError, "cross-identity"):
            self.turn(evidence=(self.evidence(actor="agent-b"),))

    def test_cross_subject_evidence_rejected(self):
        with self.assertRaisesRegex(ValueError, "cross-identity"):
            self.turn(evidence=(self.evidence(subject="user-other"),))

    def test_other_mind_inference_is_never_direct_fact_or_consent(self):
        plan = plan_interaction(self.verbal, self.turn(
            evidence=(self.evidence(ClaimKind.OTHER_MIND_INFERENCE),),
        ))
        self.assertEqual(plan.classified_claims[0].standing, ClaimStanding.INFERENCE_ONLY)
        self.assertTrue(plan.classified_claims[0].may_influence_tone)
        self.assertFalse(plan.classified_claims[0].establishes_consent)
        self.assertFalse(plan.permission_to_act)

    def test_inferred_consent_cannot_grant_permission(self):
        plan = plan_interaction(self.verbal, self.turn(
            evidence=(self.evidence(ClaimKind.CONSENT_OR_PREFERENCE_STATE),),
        ))
        self.assertEqual(plan.classified_claims[0].standing, ClaimStanding.INFERENCE_ONLY)
        self.assertFalse(plan.classified_claims[0].may_influence_tone)
        self.assertFalse(plan.classified_claims[0].establishes_consent)
        self.assertFalse(plan.permission_to_act)

    def test_even_direct_consent_statement_does_not_grant_tool_authority(self):
        plan = plan_interaction(self.verbal, self.turn(
            evidence=(self.evidence(ClaimKind.CONSENT_OR_PREFERENCE_STATE, EvidenceKind.DIRECT_STATEMENT),),
        ))
        self.assertEqual(plan.classified_claims[0].standing, ClaimStanding.DIRECT_CLAIM_UNVERIFIED)
        self.assertFalse(plan.classified_claims[0].establishes_consent)
        self.assertFalse(plan.permission_to_act)

    def test_forged_authority_constructor_rejected(self):
        with self.assertRaises(TypeError):
            SocialPlan(
                actor_id="agent-a", subject_id="user-c", answer_target="Q",
                answer_literal_request_first=True, terminology_suggestion=None,
                register=Register.DIRECT, humor_allowed=False,
                classified_claims=(), permission_to_act=True,
            )
        with self.assertRaises(TypeError):
            ClassifiedClaim(ClaimKind.OTHER_MIND_INFERENCE,
                            ClaimStanding.INFERENCE_ONLY, "source", False,
                            establishes_consent=True)

    def test_self_report_is_not_another_person_report(self):
        with self.assertRaisesRegex(ValueError, "self-report"):
            self.evidence(ClaimKind.OTHER_MIND_INFERENCE, EvidenceKind.AUTHORED_SELF_REPORT)

    def test_self_appraisal_requires_actor_as_subject(self):
        with self.assertRaisesRegex(ValueError, "self-appraisal"):
            self.evidence(ClaimKind.SELF_APPRAISAL, EvidenceKind.AUTHORED_SELF_REPORT)

    def test_self_appraisal_is_recognized_only_as_reported_stance(self):
        own = self.evidence(ClaimKind.SELF_APPRAISAL, EvidenceKind.AUTHORED_SELF_REPORT, subject="agent-a")
        turn = Interaction("agent-a", "agent-a", "What do I value?", InteractionKind.GENERAL, (own,))
        plan = plan_interaction(self.verbal, turn)
        self.assertEqual(plan.classified_claims[0].standing, ClaimStanding.REPORTED_STANCE)
        self.assertFalse(plan.classified_claims[0].establishes_consent)

    def test_explicit_correction_does_not_establish_another_mind(self):
        with self.assertRaises(ValueError):
            self.evidence(ClaimKind.OTHER_MIND_INFERENCE, EvidenceKind.EXPLICIT_CORRECTION)

    def test_direct_correction_preserved(self):
        item = self.evidence(ClaimKind.CONSENT_OR_PREFERENCE_STATE, EvidenceKind.EXPLICIT_CORRECTION)
        plan = plan_interaction(self.verbal, self.turn(kind=InteractionKind.CORRECTION, evidence=(item,)))
        self.assertEqual(plan.classified_claims[0].standing, ClaimStanding.CURRENT_CORRECTION)
        self.assertEqual(plan.register, Register.DIRECT)
        self.assertFalse(plan.permission_to_act)

    def test_explicit_correction_supersedes_old_social_cue(self):
        inferred = self.evidence(
            ClaimKind.RELATIONSHIP_STATE_INFERENCE, EvidenceKind.INFERENCE,
        )
        corrected = self.evidence(
            ClaimKind.RELATIONSHIP_STATE_INFERENCE, EvidenceKind.EXPLICIT_CORRECTION,
        )
        old = plan_interaction(
            self.verbal, self.turn(evidence=(inferred,)),
        )
        new = plan_interaction(
            self.verbal, self.turn(evidence=(inferred, corrected)),
        )
        self.assertTrue(old.classified_claims[0].may_influence_tone)
        self.assertEqual(new.classified_claims[0].standing, ClaimStanding.INFERENCE_ONLY)
        self.assertFalse(new.classified_claims[0].may_influence_tone)
        self.assertEqual(new.classified_claims[1].standing, ClaimStanding.CURRENT_CORRECTION)

    def test_correction_is_scoped_to_same_kind_not_all_observations(self):
        old_social = self.evidence(
            ClaimKind.RELATIONSHIP_STATE_INFERENCE, EvidenceKind.INFERENCE,
        )
        different = self.evidence(
            ClaimKind.CONSENT_OR_PREFERENCE_STATE, EvidenceKind.EXPLICIT_CORRECTION,
        )
        plan = plan_interaction(
            self.verbal, self.turn(evidence=(old_social, different)),
        )
        self.assertTrue(plan.classified_claims[0].may_influence_tone)

    def test_sensitive_context_disables_jokes(self):
        plan = plan_interaction(self.playful, self.turn(actor="agent-b", kind=InteractionKind.SENSITIVE))
        self.assertEqual(plan.register, Register.GENTLE)
        self.assertFalse(plan.humor_allowed)

    def test_casual_humor_requires_explicit_profile_preference(self):
        direct = plan_interaction(self.verbal, self.turn(kind=InteractionKind.CASUAL))
        playful = plan_interaction(self.playful, self.turn(actor="agent-b", kind=InteractionKind.CASUAL))
        self.assertFalse(direct.humor_allowed)
        self.assertTrue(playful.humor_allowed)

    def test_profile_validation_fail_closed(self):
        for bad in ("", "UPPER", "user id", "../other"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                ActorProfile(bad, Register.DIRECT)
        with self.assertRaises(ValueError):
            ActorProfile("agent-a", "DIRECT")  # type: ignore[arg-type]

    def test_blank_source_and_malformed_evidence_rejected(self):
        with self.assertRaises(ValueError):
            SocialEvidence("agent-a", "user-c", ClaimKind.DIRECT_RELATIONAL_FACT,
                           EvidenceKind.DIRECT_STATEMENT, "explicit", "")
        with self.assertRaises(ValueError):
            Interaction("agent-a", "user-c", "  ", InteractionKind.GENERAL)

    def test_evidence_container_is_immutable_and_typed(self):
        with self.assertRaises(ValueError):
            Interaction("agent-a", "user-c", "Q", InteractionKind.GENERAL, [])
        with self.assertRaises(ValueError):
            Interaction("agent-a", "user-c", "Q", InteractionKind.GENERAL, ("not evidence",))

    def test_models_are_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            self.verbal.actor_id = "other"
        plan = plan_interaction(self.verbal, self.turn())
        with self.assertRaises(FrozenInstanceError):
            plan.answer_target = "substitute premise"

    def test_planner_does_not_mint_new_relational_truth(self):
        evidence = self.evidence(ClaimKind.DIRECT_RELATIONAL_FACT, EvidenceKind.DIRECT_STATEMENT)
        plan = plan_interaction(self.verbal, self.turn(evidence=(evidence,)))
        self.assertEqual(plan.classified_claims[0].standing, ClaimStanding.DIRECT_CLAIM_UNVERIFIED)
        self.assertFalse(plan.classified_claims[0].may_influence_tone)


if __name__ == "__main__":
    unittest.main()
