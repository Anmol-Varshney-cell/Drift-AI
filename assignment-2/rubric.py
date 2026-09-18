"""
Evaluation Rubric and Criteria for Assignment 2: Multi-Agent Task with Review.
Defines concrete, explainable criteria for Agent B (Reviewer) to evaluate Agent A's code attempt.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class Criterion:
    id: str
    name: str
    description: str
    pass_threshold: str

REVIEW_RUBRIC: List[Criterion] = [
    Criterion(
        id="C1_ALGORITHM_CORRECTNESS",
        name="Token Bucket Mathematical Correctness",
        description="Correct implementation of time-based replenishment: tokens = min(capacity, current + elapsed * rate). Tokens correctly deducted upon successful consumption.",
        pass_threshold="Must handle time delta calculation using monotonic clock and cap tokens at maximum capacity."
    ),
    Criterion(
        id="C2_THREAD_SAFETY",
        name="Concurrency & Thread-Safety",
        description="State access and mutations (last_updated, current_tokens) must be synchronized using threading.Lock or threading.RLock.",
        pass_threshold="Must wrap token replenishment and consumption within a thread lock context."
    ),
    Criterion(
        id="C3_INPUT_VALIDATION_EDGE_CASES",
        name="Input Validation & Edge Case Handling",
        description="Must defensively validate inputs: capacity > 0, fill_rate > 0, requested tokens >= 0. Must reject invalid configurations with ValueError.",
        pass_threshold="Explicit checks and descriptive exceptions for invalid numeric parameters."
    ),
    Criterion(
        id="C4_TYPE_HINTS_AND_DOCUMENTATION",
        name="Type Annotations & Docstrings",
        description="Comprehensive PEP 484 type hints on __init__ and public methods, accompanied by clear docstrings detailing parameters, return values, and behavior.",
        pass_threshold="Zero missing type hints on signatures and non-empty class/method docstrings."
    ),
    Criterion(
        id="C5_INTERFACE_ERGONOMICS_TESTABILITY",
        name="Interface Ergonomics & Testability",
        description="Clean, intuitive public API (e.g., allow_request() / consume()) and support for injecting a custom monotonic time source for testability.",
        pass_threshold="Simple boolean consumption method and injectable time function."
    )
]

def format_rubric_prompt() -> str:
    lines = ["Review Rubric (All 5 criteria must pass for an APPROVED verdict):"]
    for c in REVIEW_RUBRIC:
        lines.append(f"- [{c.id}] {c.name}: {c.description} (Standard: {c.pass_threshold})")
    return "\n".join(lines)
