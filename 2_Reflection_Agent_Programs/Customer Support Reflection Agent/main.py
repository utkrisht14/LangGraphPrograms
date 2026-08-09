from dotenv import load_dotenv

# Load environment variables before graph.py imports nodes.py and creates the model.
load_dotenv()

from graph import support_agent  # noqa: E402


def main() -> None:
    customer_message = """
    Hi, I bought a wireless keyboard 20 days ago.
    A few keys have already stopped working.
    Can I get my money back?
    """

    support_policy = """
    Company return policy:
    
    - Defective products reported within 30 days are eligible for either
      a replacement or a full refund.
    - The customer must provide the order number before a refund or
      replacement can be processed.
    - Refunds are returned to the original payment method.
    - Do not claim that a refund has already been issued.
    """

    initial_state = {
        "customer_message": customer_message,
        "support_policy": support_policy,
        "draft_response": "",
        "critique": "",
        "approved": False,
        "iteration": 0,
    }

    result = support_agent.invoke(initial_state)

    print("\n" + "=" * 60)
    print("FINAL CUSTOMER RESPONSE")
    print("=" * 60)
    print(result['draft_response'])

    print("\n" + "=" * 60)
    print("REFLECTION RESULT")
    print("=" * 60)
    print(f"Approved: {result['approved']}")
    print(f"Attempts: {result['iteration']}")
    print(f"Last reviewer feedback: {result['critique']}")


if __name__ == "__main__":
    main()
