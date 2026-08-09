# Customer Support Reflection Agent

A small real-world LangGraph example that drafts a customer-support reply, reviews it against company policy, and revises it when necessary.

## Flow

```text
START
  |
  v
Generate draft
  |
  v
Review draft
  |
  +---- approved --------------------> END
  |
  +---- not approved + attempts left
                    |
                    v
                 Revise
                    |
                    +--------> Review
```

The graph makes at most **3 drafting attempts**.

## Setup

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, add your API key, then run:

```bash
python main.py
```

## Files

- `state.py` - shared LangGraph state.
- `nodes.py` - generator, reviewer/reflection, and revision nodes.
- `graph.py` - edges, conditional routing, and the reflection loop.
- `main.py` - realistic input and graph invocation.

The reviewer uses structured output (`approved` + `feedback`) instead of fragile free-text parsing.
