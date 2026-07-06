# AI Interview Coach — P1

A tiny command-line app that turns any topic into a mock technical interview. It
generates questions with an LLM, lets you answer them, and streams back specific,
graded coaching feedback.

It's built as a teaching project: every file demonstrates one core concept of
building *reliable* software on top of an unreliable LLM.

## What it does

1. You type a topic (e.g. "Python decorators").
2. It asks the model for **exactly 5 questions** that escalate in difficulty, each
   with a model answer and a few follow-ups.
3. For each question you type your answer — or press Enter to skip and just read
   the reference answer.
4. If you answered, a coach **streams back a critique**: a score out of 10, what
   you got right, what was missing, and one concrete tip.

## Concepts by file

| File | Concept it teaches |
| --- | --- |
| [main.py](main.py) | **Orchestration.** The interactive CLI loop that ties everything together; contains no LLM logic itself. |
| [llm.py](llm.py) | **Provider isolation.** The *only* file that talks to a model provider. Swap models or vendors here without touching the rest of the app. |
| [models.py](models.py) | **The data contract.** Pydantic schemas that define the exact shape you demand back from the model. |
| [coach.py](coach.py) | **Prompt craft + reliability.** Structured output with a validate-and-retry loop for question generation, and streaming feedback engineered to force *specific* critique. |

## Key ideas worth understanding

- **Validate-and-retry** (`coach.py`): the model's raw output is never trusted. It's
  parsed, checked against the Pydantic schema, and if it's malformed the validation
  error is handed *back to the model* so it can self-correct — up to 3 attempts. This
  is what turns "works once in a demo" into "works every run."
- **Schema-first design** (`models.py`): the output shape is declared once and
  enforced, so the rest of the code works with clean Python objects, not fragile strings.
- **Temperature per job**: `0.7` for generating questions (a little creativity helps)
  vs. `0.4` for grading (feedback should be consistent and grounded).
- **Streaming**: grading feedback prints token by token, so you watch the coach "think"
  in real time.

## Setup

Requires Python 3.13+.

```bash
# 1. Install dependencies (using uv)
uv sync

# or with pip
pip install -e .

# 2. Configure your environment
cp .env.example .env
```

Then edit `.env` and set:

```
OPENAI_API_KEY=sk-...        # your OpenAI API key
OPENAI_MODEL=gpt-4o-mini     # any chat model; gpt-4o-mini is a good default
```

## Usage

```bash
python main.py
```

Optional flags:

```bash
# Turn the creativity dial for question generation (~0.0 focused, ~1.2 wild)
python main.py --temperature 1.0
```

Run it a few times with different `--temperature` values to feel how it changes the
questions you get.
