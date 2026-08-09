# SmartReplyReflexion

A beginner-friendly real-world LangGraph project demonstrating the
**Reflexion pattern** with a customer-support reply assistant.

## Workflow

```text
START
  |
  v
Generate reply
  |
  v
Review reply
  |
  +---- Approved ----------------------> END
  |
  +---- Not approved
            |
            v
     Store feedback
            |
            v
   Generate again using
     feedback history
            |
            +--------------------------> Review
```

The workflow stops after a maximum of **3 generated drafts**.

## Why this is Reflexion

The important state field is:

```python
feedback_history: list[str]
```

When an attempt fails, its feedback is stored.

The next generation receives all earlier feedback:

```text
Attempt 1
   -> feedback 1

Attempt 2
   -> uses feedback 1
   -> feedback 2

Attempt 3
   -> uses feedback 1 + feedback 2
```

So the agent is not merely reviewing an answer. It uses previous
verbal feedback as experience for its next attempt.

## Files

```text
SmartReplyReflexion/
├── state.py
├── nodes.py
├── graph.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then add your API key:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5-nano
```

Run:

```bash
python main.py
```
