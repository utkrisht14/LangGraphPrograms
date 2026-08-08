# Reflection Agents

A **Reflection Agent** is an agent that does not immediately accept its first answer as final. It creates an answer, **reviews or critiques its own output**, and then improves it.

A simple flow looks like this:

```text
User question
    ↓
Generate answer
    ↓
Critique / Reflect
    ↓
Is the answer good enough?
   ├── Yes → Final answer
   └── No  → Revise answer
                ↓
             Reflect again
```

The key idea is:

```text
Generate → Evaluate → Improve
```

Instead of:

```text
Generate → Return
```

---

## Why do we need reflection?

LLMs can make mistakes even when they know the correct information. They may:

- miss part of the question
- give an incomplete answer
- make reasoning errors
- produce weak code
- forget a constraint
- use poor structure
- hallucinate something
- fail to use tool results properly

Reflection gives the system a second chance to inspect the output before returning it.

For example, suppose you ask:

```text
Write a Python function to calculate factorial.
Handle negative numbers and zero.
```

The first agent may generate:

```python
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

This works for `0`, but it does not handle negative numbers.

A reflection step could inspect the answer and say:

```text
Problem:
The function does not reject negative numbers.
```

Then the generation agent revises it:

```python
def factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")

    result = 1

    for i in range(1, n + 1):
        result *= i

    return result
```

That is reflection in practice.

---

## Reflection agents in LangGraph

LangGraph is particularly suitable for reflection because reflection naturally creates a **loop**.

```text
Generate
   ↓
Reflect
   ↓
Good enough?
   ├── Yes → END
   └── No
        ↓
      Generate
```

That loop is exactly the kind of workflow LangGraph is designed to manage.

You might have two nodes:

```python
def generate(state):
    ...
```

and:

```python
def reflect(state):
    ...
```

Then your graph could look like:

```text
START
  ↓
generate
  ↓
reflect
  ↓
should_continue?
   ├── generate
   └── END
```

---

## Generator vs Reflection Agent

You can think of them as two roles.

```text
Generator Agent
      ↓
"Here is my answer."

Reflection Agent
      ↓
"Let me check whether that answer is actually good."
```

The generator creates.

The reflector evaluates.

For example:

```text
Generator:
"The capital of Australia is Sydney."

Reflector:
"This is incorrect. Australia's capital is Canberra."

Generator:
"The capital of Australia is Canberra."
```

In a real application, the reflection step usually uses a more detailed rubric instead of simply asking "is this correct?"

For example:

```text
Evaluate the answer for:

1. Correctness
2. Completeness
3. Relevance
4. Unsupported claims
5. Whether all user requirements were followed
```

---

## One model or two models?

You don't necessarily need two separate LLMs.

You can use the same model twice with different prompts:

```text
Same LLM
   │
   ├── Prompt 1:
   │   "Generate an answer"
   │
   └── Prompt 2:
       "Critique this answer"
```

Or you can use different models:

```text
GPT model → Generate

Claude/Gemini/another model → Critique
```

Sometimes using a different model as the critic can reduce the chance that the same model repeats its original mistake.

---

## Example State

A reflection graph might store:

```python
class State(TypedDict):
    question: str
    answer: str
    critique: str
    iteration: int
```

Initially:

```python
{
    "question": "Explain recursion",
    "answer": "",
    "critique": "",
    "iteration": 0
}
```

After generation:

```python
{
    "question": "Explain recursion",
    "answer": "Recursion is...",
    "critique": "",
    "iteration": 1
}
```

After reflection:

```python
{
    "question": "Explain recursion",
    "answer": "Recursion is...",
    "critique": "The explanation needs a base-case example.",
    "iteration": 1
}
```

Then the generator uses both:

```text
Original question
+
Previous answer
+
Critique
```

to make a better response.

---

## A simple LangGraph structure

Conceptually:

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)

builder.add_node("generate", generate)
builder.add_node("reflect", reflect)

builder.add_edge(START, "generate")
builder.add_edge("generate", "reflect")

builder.add_conditional_edges(
    "reflect",
    should_continue,
    {
        "retry": "generate",
        "done": END
    }
)

graph = builder.compile()
```

The important part is:

```python
"retry": "generate"
```

That creates the loop.

```text
generate
   ↓
reflect
   ↓
generate
   ↓
reflect
   ↓
END
```

---

## Why not reflect forever?

This is important.

If you create:

```text
Generate → Reflect → Generate → Reflect
```

with no limit, the agent could loop forever.

Usually you add something like:

```python
if state["iteration"] >= 3:
    return "done"
```

So you allow perhaps:

```text
Maximum 2–3 revisions
```

Reflection has a cost because every reflection is another LLM call.

If one call costs:

```text
Generate = 1 LLM call
```

reflection might turn it into:

```text
Generate
Reflect
Generate again
Reflect again

= 4 LLM calls
```

So reflection improves quality, but can increase:

- latency
- token usage
- API cost

---

## When reflection is useful

Reflection is especially valuable when the quality of the result matters.

For example:

```text
Coding agents
Research agents
RAG agents
SQL generation
Complex reasoning
Report generation
Planning agents
Data analysis
```

A coding agent could work like:

```text
Write code
   ↓
Review code
   ↓
Run tests
   ↓
Tests fail?
   ├── Yes → Fix code
   └── No → Finish
```

This is actually stronger than pure self-reflection because the agent has **external feedback** from tests.

---

## Reflection vs Tool Feedback

There are two related ideas.

### Self-reflection

The LLM evaluates itself:

```text
LLM generates code
      ↓
LLM reviews code
```

### External feedback

The agent actually checks something:

```text
LLM generates code
      ↓
Run unit tests
      ↓
Tests fail
      ↓
LLM fixes code
```

External feedback is often more reliable.

For example:

```text
Reflection:
"I think my SQL query is correct."

versus

Database:
"Syntax error near JOIN"
```

The second one gives much stronger evidence.

Modern agents often combine both:

```text
Generate
   ↓
Reflect
   ↓
Use tool/test/retriever
   ↓
Evaluate
   ↓
Improve
```

---

## Reflection vs ReAct

These two concepts are related but different.

### ReAct

**ReAct** means:

```text
Reason
↓
Act / use tool
↓
Observe result
↓
Reason again
```

Example:

```text
Question
↓
Need weather information
↓
Call weather API
↓
Observe result
↓
Answer
```

### Reflection

Reflection means:

```text
Generate
↓
Critique generated result
↓
Improve it
```

You can combine them:

```text
Reason
↓
Use tool
↓
Generate answer
↓
Reflect
↓
Need another tool?
↓
Use tool
↓
Improve answer
```

That is a much more capable agent.

---

## The main idea to remember

Think of a normal agent as a **student answering an exam question**:

```text
Read question
↓
Write answer
↓
Submit
```

A reflection agent behaves like a careful student:

```text
Read question
↓
Write answer
↓
Read the answer again
↓
Find mistakes
↓
Correct them
↓
Submit
```

That is essentially what reflection adds.

And this is one reason LangGraph becomes useful: once you start adding **reflection, retries, evaluation and loops**, your agent stops looking like a simple LangChain pipeline and starts looking like a real workflow graph.
