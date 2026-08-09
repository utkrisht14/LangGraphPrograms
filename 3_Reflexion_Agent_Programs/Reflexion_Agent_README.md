# Reflexion Agents — Learning Notes

> A beginner-friendly guide to understanding **Reflexion agents**, how they learn from mistakes, how they differ from ordinary reflection, and why the original paper describes the method as **“Verbal Reinforcement Learning.”**

---

## 1. Learning Goals

After reading this note, you should be able to explain:

- What a Reflexion agent is.
- Why Reflexion was introduced.
- The difference between **reflection** and **Reflexion**.
- The roles of the **Actor**, **Evaluator**, **Self-Reflection model**, and **Memory**.
- What **verbal reinforcement learning** means in this context.
- Why Reflexion does **not normally update the LLM's model weights**.
- How the Reflexion loop works.
- When Reflexion is useful and when it is unnecessary.
- How the idea maps naturally to a framework such as LangGraph.

---

# 2. What Is a Reflexion Agent?

A **Reflexion agent** is an LLM-based agent that improves future attempts by examining feedback from previous attempts, converting that feedback into a useful **natural-language reflection**, storing the reflection in memory, and using it during later trials.

The core idea is:

```text
Try
 ↓
Evaluate
 ↓
Reflect on what went wrong
 ↓
Store the lesson
 ↓
Try again using the lesson
```

Instead of simply producing a new answer after failure, the agent asks:

> **What did I learn from the previous attempt, and how should that change my next attempt?**

This makes Reflexion a form of **learning through experience without retraining the underlying LLM after every mistake**.

---

# 3. Why Do We Need Reflexion?

A normal LLM interaction often looks like:

```text
User Request
     ↓
    LLM
     ↓
   Answer
     ↓
    END
```

If the answer is wrong, incomplete, or poorly reasoned, the system may simply fail.

A Reflexion-style agent introduces a feedback loop:

```text
User Request
     ↓
Generate Attempt
     ↓
Evaluate Attempt
     ↓
Was it successful?
   /          \
 Yes           No
  ↓             ↓
 END         Reflect
                ↓
          Save the lesson
                ↓
          Try again
```

This is useful because many agent tasks involve:

- trial and error,
- tool usage,
- planning,
- coding,
- multi-step reasoning,
- interacting with external environments,
- correcting failures.

The first attempt does not always need to be perfect if the agent has a reliable mechanism for learning from what happened.

---

# 4. The Core Reflexion Loop

A simple Reflexion loop can be summarized as:

```text
ACT → EVALUATE → REFLECT → REMEMBER → RETRY
```

Each stage has a different responsibility.

---

## 4.1 Actor

The **Actor** performs the task.

Examples:

- answer a question,
- generate code,
- choose an action,
- call tools,
- navigate an environment,
- produce a plan.

Example:

```text
Task:
Write a Python function that validates an email address.

Actor:
Produces the first implementation.
```

The Actor does not have to be a special model. It can be a normal LLM prompted to perform the task.

---

## 4.2 Evaluator

The **Evaluator** determines how successful the Actor's attempt was.

The evaluation signal may come from:

- a test result,
- compiler output,
- an environment reward,
- an exact answer,
- another LLM,
- a human,
- a task-specific validator.

For example:

```text
Attempt:
Generated Python function

Evaluator:
3 of 5 tests passed
```

or:

```text
Evaluator:
The response is incomplete because it does not explain the refund process.
```

The important point is that the agent receives some indication of **how well the attempt performed**.

---

## 4.3 Self-Reflection Model

The **Self-Reflection model** interprets the attempt together with its feedback and produces a useful verbal lesson.

For example:

```text
Attempt:
The code failed two edge-case tests.

Feedback:
Empty strings and strings containing spaces are handled incorrectly.

Reflection:
The next implementation should explicitly validate empty input and reject
whitespace before applying the main validation logic.
```

This reflection is more useful to an LLM than simply receiving:

```text
Reward = 0
```

because it explains **what should change**.

---

## 4.4 Episodic Memory

Reflexion stores useful reflections in an **episodic memory**.

Conceptually:

```text
Memory
├── Lesson from attempt 1
├── Lesson from attempt 2
└── Lesson from attempt 3
```

The next attempt can be conditioned on these previous lessons:

```text
Original Task
+
Previous Experience
+
Reflection
        ↓
      Actor
        ↓
Better Attempt
```

The memory is important because the agent is not merely regenerating from scratch.

It is carrying forward information learned from previous trials.

---

# 5. Complete Reflexion Architecture

The original Reflexion framework can be understood through four major pieces:

```text
                    ┌──────────────────┐
                    │      Actor       │
                    │  Performs task   │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │    Evaluator     │
                    │ Scores/checks it │
                    └────────┬─────────┘
                             ↓
                       Successful?
                      /             \
                    Yes              No
                     ↓                ↓
                    END      ┌──────────────────┐
                             │ Self-Reflection  │
                             │  Extract lesson  │
                             └────────┬─────────┘
                                      ↓
                             ┌──────────────────┐
                             │ Episodic Memory  │
                             │   Store lesson   │
                             └────────┬─────────┘
                                      ↓
                                    Actor
```

The Actor, Evaluator, and Self-Reflection components may use separate models, but they do not have to.

A practical implementation might use the **same LLM with different prompts**.

For example:

```text
Same LLM
├── Prompt 1 → Act as Actor
├── Prompt 2 → Act as Evaluator
└── Prompt 3 → Act as Reflector
```

---

# 6. A Simple Real-World Example

Suppose the task is:

> Write a customer-support response explaining how to reset a password.

### Attempt 1 — Actor

```text
You can reset your password from the login page.
```

### Evaluation

```text
Not approved.

Problems:
- It does not explain where the reset link is.
- It does not mention checking the email inbox.
- It does not explain what to do if the email does not arrive.
```

### Reflection

```text
The previous response was too short. The next response should explain:
1. Where to select "Forgot password."
2. That a reset link will be sent by email.
3. What the user should check if the email is missing.
```

### Attempt 2 — Actor uses the reflection

```text
Select "Forgot password" on the login page and enter your registered email
address. A password-reset link will be sent to your inbox. If you do not see
the email, check your spam folder and verify that you entered the email
associated with your account.
```

### Evaluation

```text
Approved.
```

The important difference is that Attempt 2 was not just another random generation.

It was explicitly guided by the lesson learned from Attempt 1.

---

# 7. Reflection vs Reflexion

These terms are related but should not be treated as exactly the same thing.

| Concept | Reflection | Reflexion |
|---|---|---|
| Meaning | General technique of reviewing one's own output | A specific agent-learning framework introduced by Shinn et al. |
| Main idea | Critique and improve an answer | Learn from trial feedback using verbal reflections |
| Memory required? | Not necessarily | Episodic reflection memory is a central part of the framework |
| Multiple trials? | Often, but not required | Designed around repeated trials |
| Evaluator | May or may not be explicit | Evaluation/feedback is part of the learning loop |
| Reflection stored? | Not necessarily | Reflections are carried forward as experience |
| Model weights updated? | Usually not | Reflexion reinforces behavior through context/memory rather than weight updates |
| Goal | Improve the current output | Improve decision-making in subsequent trials |

A useful mental model is:

```text
Reflection
    =
"Let me review my answer."

Reflexion
    =
"Let me evaluate what happened, extract a lesson,
remember that lesson, and use it in my next trial."
```

Therefore:

> **Every Reflexion agent uses reflection, but not every agent that reflects is implementing the Reflexion framework.**

---

# 8. Why Is It Called “Reflexion”?

**Reflexion** is the name given to the framework by the paper's authors.

The important idea is repeated learning from experience:

```text
Experience
    ↓
Feedback
    ↓
Reflection
    ↓
Memory
    ↓
Improved future behavior
```

It is useful to treat **Reflexion** with a capital **R** as the name of the specific framework, while **reflection** is the broader technique.

---

# 9. Why Is the Paper Titled
# “Reflexion: Language Agents with Verbal Reinforcement Learning”?

The title contains three important ideas:

```text
Reflexion
+
Language Agents
+
Verbal Reinforcement Learning
```

Let's break them down.

---

## 9.1 “Language Agents”

A language agent uses an LLM as part of an agent that can perform goal-directed actions.

It may interact with:

- APIs,
- tools,
- compilers,
- search systems,
- games,
- environments,
- databases,
- other software.

So the paper is not only about generating better text.

It is about **LLMs acting as agents and learning from what happens when they act**.

---

## 9.2 “Reinforcement”

In traditional Reinforcement Learning (RL), an agent commonly interacts with an environment and receives a reward signal:

```text
State
  ↓
Action
  ↓
Environment
  ↓
Reward
  ↓
Update policy
```

For example:

```text
Good action → +1
Bad action  → -1
```

The learning algorithm then changes the policy or model parameters so future actions improve.

---

## 9.3 “Verbal”

A scalar reward such as:

```text
Reward = 0
```

tells an agent that something was wrong, but it does not explain **why**.

An LLM can benefit from a richer signal such as:

```text
The attempt failed because the solution assumed the input list was always
non-empty. On the next attempt, handle the empty-list case before processing
the remaining elements.
```

That is a **verbal**, natural-language signal.

---

# 10. What Does “Verbal Reinforcement Learning” Mean?

The phrase can initially be confusing because Reflexion is **not simply standard deep reinforcement learning applied to an LLM**.

The key distinction is:

### Traditional RL

```text
Experience
    ↓
Reward
    ↓
Optimization
    ↓
Change model/policy parameters
```

### Reflexion

```text
Experience
    ↓
Feedback / Reward
    ↓
Natural-language reflection
    ↓
Store reflection in memory
    ↓
Put reflection into future context
    ↓
Improved next attempt
```

In Reflexion, the underlying LLM's weights generally remain unchanged during this trial-and-error loop.

Instead of saying:

> "Change the neural network weights because the reward was poor."

Reflexion effectively says:

> "Describe in language what went wrong, remember that description, and use it as guidance next time."

That is why the term **verbal reinforcement** is appropriate.

---

# 11. Model Weights vs Memory

This distinction is extremely important.

## Traditional training

```text
Model
 ↓
Training
 ↓
Weights change
 ↓
Updated model
```

For example:

```text
Weight 1: 0.42 → 0.45
Weight 2: 0.71 → 0.68
...
```

## Reflexion

```text
Model weights
   ↓
remain unchanged

Memory
   ↓
gets new reflection

Prompt/context
   ↓
contains learned experience
```

The "learning" therefore happens primarily through **context and memory**, rather than gradient-based parameter updates during the Reflexion loop.

---

# 12. Simple Python Example

The following example demonstrates the idea without depending on an agent framework.

```python
MAX_ATTEMPTS = 3


def generate_answer(task: str, reflection: str = "") -> str:
    """
    Generate an answer while considering lessons from a previous attempt.
    """

    # In a real application, this function would call an LLM.
    if not reflection:
        return "First attempt"

    return f"Improved attempt using this lesson: {reflection}"


def evaluate(answer: str) -> tuple[bool, str]:
    """
    Evaluate the current answer and return approval plus feedback.
    """

    # In a real application, this could use tests, rules, or another LLM.
    if answer == "First attempt":
        return False, "The answer is incomplete. Add the missing explanation."

    return True, "The answer satisfies the requirements."


reflection = ""

for attempt in range(1, MAX_ATTEMPTS + 1):

    # Actor: create an answer using any previous reflection.
    answer = generate_answer(
        task="Explain the concept.",
        reflection=reflection
    )

    # Evaluator: determine whether the attempt is good enough.
    approved, feedback = evaluate(answer)

    print(f"Attempt {attempt}: {answer}")

    # Stop when the evaluator approves the result.
    if approved:
        break

    # Reflector: convert the feedback into guidance for the next attempt.
    reflection = feedback
```

The key idea is not the exact code.

The important flow is:

```text
generate_answer()
      ↓
evaluate()
      ↓
approved?
 /         \
Yes         No
 ↓           ↓
END       reflection
              ↓
        generate_answer()
```

---

# 13. A More Realistic State

In an agent framework, you may keep shared state such as:

```python
from typing import TypedDict


class ReflexionState(TypedDict):
    task: str
    answer: str
    feedback: str
    reflections: list[str]
    approved: bool
    iteration: int
```

The state can be thought of as the agent's current working information:

```text
ReflexionState
│
├── task
├── answer
├── feedback
├── reflections
├── approved
└── iteration
```

Example:

```python
state = {
    "task": "Write a safe file parser.",
    "answer": "...",
    "feedback": "Missing exception handling.",
    "reflections": [
        "Validate input before parsing.",
        "Handle malformed files explicitly."
    ],
    "approved": False,
    "iteration": 2
}
```

The agent can use `reflections` when producing its next attempt.

---

# 14. How Reflexion Maps to LangGraph

Reflexion is a natural fit for LangGraph because the workflow contains:

- shared state,
- multiple nodes,
- conditional routing,
- loops,
- stopping conditions.

A conceptual LangGraph design could be:

```text
START
  ↓
ACTOR
  ↓
EVALUATOR
  ↓
Approved?
 /       \
Yes       No
 ↓         ↓
END     REFLECT
           ↓
         ACTOR
```

Possible nodes:

```text
"actor"      → generates an attempt
"evaluate"   → checks the attempt
"reflect"    → produces verbal feedback
```

Possible state:

```text
task
answer
feedback
reflections
approved
iteration
```

Possible conditional routing:

```text
evaluate
   ↓
route_after_review()
   ├── END
   └── reflect
```

This is one of the reasons graph-based agent orchestration is useful: a Reflexion workflow is **cyclic**, not purely linear.

---

# 15. Why Use a Maximum Number of Attempts?

A Reflexion loop should normally have a stopping condition.

For example:

```python
MAX_ATTEMPTS = 3
```

Without a limit:

```text
Act
 ↓
Evaluate
 ↓
Reflect
 ↓
Act
 ↓
Evaluate
 ↓
Reflect
 ↓
...
```

the agent could continue indefinitely if the evaluator never approves the answer.

A safer design is:

```text
                 Evaluator
                     ↓
             Is it approved?
              /           \
            Yes            No
             ↓              ↓
            END      Max attempts?
                      /          \
                    Yes           No
                     ↓             ↓
                    END          Reflect
```

Attempt limits help control:

- API cost,
- latency,
- infinite loops,
- repeated unproductive revisions.

---

# 16. Reflexion with Tools

Reflexion becomes especially useful when an agent interacts with external tools.

Example:

```text
Task:
Find information satisfying several constraints.

Agent:
Uses search tool
     ↓
Produces answer
     ↓
Evaluator:
One required constraint was ignored
     ↓
Reflection:
"On the next search, include constraint X and verify it before answering."
     ↓
Agent searches again
```

The loop becomes:

```text
Reason
  ↓
Act
  ↓
Observe
  ↓
Evaluate
  ↓
Reflect
  ↓
Act again
```

---

# 17. Reflexion vs ReAct

These two concepts solve different problems.

## ReAct

ReAct focuses on combining reasoning and actions:

```text
Reason
  ↓
Act
  ↓
Observe
  ↓
Reason
```

Example:

```text
"I need the weather."
       ↓
Call weather tool
       ↓
Observe result
       ↓
Produce answer
```

## Reflexion

Reflexion focuses on learning from unsuccessful trials:

```text
Attempt
   ↓
Evaluate
   ↓
Reflect
   ↓
Remember
   ↓
Retry
```

They are **not mutually exclusive**.

A Reflexion system may use a ReAct agent as its Actor:

```text
             Reflexion
                 │
        ┌────────┴────────┐
        │                 │
      Actor            Reflection
        │
      ReAct
        │
Reason → Act → Observe
```

So Reflexion can be viewed as an improvement loop around another agent strategy.

---

# 18. Reflection vs Retry

Another useful distinction:

## Simple Retry

```text
Attempt 1 failed
      ↓
Try again
```

The second attempt may repeat the same mistake.

## Reflexion

```text
Attempt 1 failed
      ↓
Determine WHY
      ↓
Write lesson
      ↓
Use lesson in Attempt 2
```

Therefore, Reflexion is not valuable merely because it retries.

Its value comes from **learning what to change before retrying**.

---

# 19. Where Can the Feedback Come From?

Reflexion does not require only one kind of evaluator.

Feedback may come from:

### Environment

```text
Game score
Task completion signal
API response
```

### Programmatic validation

```text
Unit tests
Compiler errors
Schema validation
Assertions
```

### Human feedback

```text
"The answer is too technical."
```

### Another LLM

```text
"The proposed solution does not address the second requirement."
```

### The same LLM in an evaluator role

```text
Actor prompt     → generate
Evaluator prompt → critique
Reflector prompt → extract lesson
```

This flexibility is one of the useful properties of the approach.

---

# 20. Example: Coding Agent

Reflexion is particularly intuitive for programming.

```text
Task
 ↓
Generate code
 ↓
Run tests
 ↓
Tests pass?
 /       \
Yes       No
 ↓         ↓
END     Read failures
           ↓
        Reflect
           ↓
     "I forgot to handle
      negative inputs."
           ↓
      Generate fix
           ↓
        Run tests
```

This works well because compiler output and tests provide relatively objective feedback.

---

# 21. Example: Research Agent

A research workflow might look like:

```text
Research question
      ↓
Search and answer
      ↓
Evaluator checks:
- Are claims supported?
- Are required sources included?
- Are important aspects missing?
      ↓
Reflection:
"Evidence for the second claim is weak.
Search specifically for primary evidence."
      ↓
Research again
```

---

# 22. Example: Customer-Support Agent

```text
Customer request
      ↓
Draft response
      ↓
Evaluator checks:
- Correct?
- Complete?
- Policy compliant?
- Professional?
      ↓
Reflection
      ↓
Revise
```

This can help prevent an agent from sending an incomplete first draft.

---

# 23. Good Use Cases

Reflexion is useful when:

- the first attempt may fail,
- feedback is available,
- the task can be retried,
- improvement can be measured,
- the agent can benefit from previous mistakes.

Good examples include:

- coding agents,
- debugging,
- tool-using agents,
- complex reasoning,
- planning,
- research,
- support workflows,
- game-playing agents,
- multi-step decision-making.

---

# 24. When Reflexion May Be Unnecessary

Reflexion adds:

- extra LLM calls,
- additional latency,
- additional tokens,
- more state management,
- more workflow complexity.

For a simple request such as:

```text
What is 2 + 2?
```

a loop like:

```text
Generate
 ↓
Evaluate
 ↓
Reflect
 ↓
Regenerate
```

would usually be unnecessary.

Use Reflexion when the potential quality improvement justifies the additional cost and complexity.

---

# 25. Important Limitations

Reflexion is powerful, but it is not guaranteed to improve every attempt.

## 25.1 Bad reflection can reinforce bad reasoning

If the evaluator gives incorrect feedback, the next attempt can become worse.

```text
Wrong evaluation
      ↓
Wrong reflection
      ↓
Wrong lesson
      ↓
Worse attempt
```

## 25.2 The LLM may repeat mistakes

Natural-language feedback does not guarantee that the Actor will follow it correctly.

## 25.3 Memory can become noisy

Too many stored reflections may:

- consume context,
- contradict each other,
- distract the model.

Memory should therefore be managed deliberately.

## 25.4 More attempts mean more cost

A three-attempt system can require several LLM calls:

```text
Actor
Evaluator
Reflector
Actor
Evaluator
...
```

The workflow should have clear stopping conditions.

---

# 26. Reflexion in One Example

Imagine a human developer.

### First attempt

```text
Developer writes code.
```

### Feedback

```text
Tests fail.
```

### Reflection

```text
"I assumed the list would always contain an element.
I need to handle empty lists."
```

### Memory

The developer remembers the mistake.

### Second attempt

```text
Developer fixes the empty-list case.
```

That human learning process is a good mental model for Reflexion:

```text
Do
 ↓
Observe
 ↓
Understand mistake
 ↓
Remember lesson
 ↓
Do better
```

---

# 27. The Most Important Difference From Traditional Reinforcement Learning

Keep this distinction in mind:

```text
Traditional RL
--------------
Reward
  ↓
Optimization
  ↓
Update parameters


Reflexion
---------
Feedback
  ↓
Verbal reflection
  ↓
Memory/context
  ↓
Improved future attempt
```

Reflexion therefore provides a way for language agents to improve through trial-and-error **without requiring a gradient update after each experience**.

---

# 28. Key Terminology

| Term | Meaning |
|---|---|
| **Actor** | Agent/model that performs the task |
| **Trajectory** | Sequence of actions/reasoning taken during a trial |
| **Evaluator** | Component that judges the result |
| **Feedback** | Signal indicating how the attempt performed |
| **Reflection** | Natural-language analysis of what should be learned |
| **Self-Reflection model** | Component that generates the verbal lesson |
| **Episodic Memory** | Stored reflections from previous experiences |
| **Trial** | One attempt at the task |
| **Reflexion** | Framework that uses evaluation, verbal reflection, and memory to improve subsequent trials |
| **Verbal Reinforcement** | Reinforcing behavior using linguistic feedback/context rather than immediate parameter updates |

---

# 29. One-Sentence Definition

> **Reflexion is an agent framework in which an LLM learns from trial-and-error by converting feedback about previous attempts into verbal reflections, storing those reflections in episodic memory, and using them to make better decisions in later trials.**

---

# 30. Five Things to Remember

If you remember only five ideas, remember these:

1. **Reflexion is more than simply retrying.**
2. **The agent evaluates previous attempts and identifies what went wrong.**
3. **The lesson is expressed in natural language.**
4. **The reflection is stored and reused as experience.**
5. **The LLM can improve across trials without changing its model weights during the Reflexion loop.**

The shortest mental model is:

```text
ACT
 ↓
EVALUATE
 ↓
REFLECT
 ↓
REMEMBER
 ↓
RETRY BETTER
```

---

# 31. Suggested Learning Order

For someone learning LLM agents and LangGraph, a useful order is:

```text
1. LLM messages and prompts
        ↓
2. Tool calling
        ↓
3. Agent state
        ↓
4. Nodes and edges
        ↓
5. Conditional edges
        ↓
6. Loops
        ↓
7. Reflection agent
        ↓
8. Reflexion + memory
        ↓
9. More advanced self-improving agents
```

Understanding **state + conditional edges + loops** makes Reflexion much easier to implement in LangGraph.

---

# 32. Original Paper

**Reflexion: Language Agents with Verbal Reinforcement Learning**

Authors: Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao.

Published at **NeurIPS 2023**.

The paper studies Reflexion across tasks including:

- sequential decision-making,
- reasoning,
- code generation.

The central idea is to reinforce language agents through **linguistic feedback and episodic reflection memory rather than weight updates during the learning loop**.

### References

- Paper (arXiv): https://arxiv.org/abs/2303.11366
- NeurIPS proceedings: https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html
- Official code repository: https://github.com/noahshinn/reflexion

---

## Final Mental Model

```text
                    REFLEXION AGENT

                        TASK
                          ↓
                    ┌───────────┐
                    │   ACTOR   │
                    └─────┬─────┘
                          ↓
                    ┌───────────┐
                    │ EVALUATOR │
                    └─────┬─────┘
                          ↓
                      Successful?
                     /           \
                   Yes            No
                    ↓              ↓
                   END       ┌────────────┐
                             │  REFLECT   │
                             └─────┬──────┘
                                   ↓
                             ┌────────────┐
                             │   MEMORY   │
                             └─────┬──────┘
                                   ↓
                                 ACTOR
                                   ↓
                             BETTER ATTEMPT
```

> **Reflexion = Experience → Feedback → Verbal Lesson → Memory → Better Future Action**
