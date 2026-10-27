"""Example of independent host-supplied identities. No actual agent is selected."""
from personification import ActorProfile, Interaction, InteractionKind, Register, plan_interaction


def main() -> None:
    request = "Is the proposition I just stated factually correct?"
    configurations = (
        ActorProfile("actor-alpha", Register.DIRECT, allow_humor=False),
        ActorProfile("actor-beta", Register.CONVERSATIONAL, allow_humor=True),
    )
    for profile in configurations:
        turn = Interaction(
            actor_id=profile.actor_id,
            subject_id="user-example",
            literal_request=request,
            kind=InteractionKind.FACT_CHECK,
        )
        plan = plan_interaction(profile, turn)
        assert plan.actor_id == profile.actor_id
        assert plan.answer_target == request
        assert plan.permission_to_act is False
        print(profile.actor_id, plan.register.value, "permission_to_act=False")


if __name__ == "__main__":
    main()
