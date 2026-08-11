from langchain_core.tools import tool

@tool
def search_company_policy(query: str) -> str:
    """
    Search company instructions stored in an external text file.
    """
    with open("company_policy.txt", "r", encoding="utf-8") as file:
        policy = file.read()

    # For this simple project, return the full policy, otherwise we could have used RAG/vector search
    return policy



@tool
def get_order_status(order_id: str) -> str:
    """
    Return the current status of a customer order.

    This is simulated data for a simple project purpose.
    """

    order = {
        "ORD1001": "Delivered 5 days ago",
        "ORD1002": "Currently being shipped",
        "ORD1003": "Delivered 45 days ago",
    }

    return order.get(order_id, "Order not found")