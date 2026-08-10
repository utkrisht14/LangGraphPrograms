from graph import reflexion_agent


def main() -> None:
    customer_message = """
    Hi, I ordered a portable Bluetooth speaker 18 days ago.
    It suddenly stopped charging. I would prefer a refund instead
    of a replacement. Can you refund it?
    """

    company_policy = """
    Return policy:
    - Defective products reported within 30 days are eligible for
      a replacement or a full refund.
    - An order number is required before a refund or replacement
      can be processed.
    - Approved refunds are returned to the original payment method.
    - Support agents must not claim that a refund has already been issued.
    """

    initial_state = {
        "customer_message": customer_message,
        "company_policy": company_policy,
        "draft_response": "",
        "latest_feedback": "",
        "feedback_history": [],
        "approved": False,
        "iteration": 0,
    }

    result = reflexion_agent.invoke(initial_state)

    print("\n" + "=" * 60)
    print("FINAL RESPONSE")
    print("=" * 60)
    print(result["draft_response"])

    print("\n" + "=" * 60)
    print("REFLEXION SUMMARY")
    print("=" * 60)
    print(f"Approved: {result['approved']}")
    print(f"Attempts: {result['iteration']}")

    print("\nLessons collected:")

    if result["feedback_history"]:
        for number, feedback in enumerate(
            result["feedback_history"],
            start=1,
        ):
            print(f"{number}. {feedback}")
    else:
        print("No revisions were required.")


if __name__ == "__main__":
    main()
