from dotenv import load_dotenv

from graph import graph

load_dotenv()

print("API_KEY=os.getenv('OPENAI_API_KEY')")

def main():
    question = """ 
    My order ORD1002 has not arrived yet.
    Can I cancel it and get a refund?
    """

    initial_state = {
        "question": question,
        "answer": "",
        "feedback": "",
        "approved": False,
        "iteration": 0
    }

    result = graph.invoke(initial_state)

    print("\n-----------------------------")
    print("FINAL ANSWER")
    print("-----------------------------")

    print(result["answer"])

    print("\nIterations:", result["iteration"])

    print("\nLast reviewer feedback:")
    print(result["feedback"])


if __name__ == "__main__":
    main()
