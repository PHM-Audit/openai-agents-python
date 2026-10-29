"""
Physics plausibility check tool (deterministic, offline).

Demonstrates wrapping a deterministic validator as a function tool so an
agent can self-verify numeric claims (unit consistency, speed-of-light
limit, probability ranges, kinematics) before presenting them.

The checker is the offline subset of the PHM engine:
    pip install git+https://github.com/PHM-Audit/phm-lite-check

Run: python examples/tools/physics_plausibility_check.py
"""

import asyncio
import json

from agents import Agent, Runner, function_tool


@function_tool
def physics_text_check(text: str) -> str:
    """Check text for physically implausible numeric claims.

    Deterministic offline checker (no network, no model calls). Scans for
    quantities with units and verifies: unit consistency, universal speed
    limit, absolute temperature floor, non-negativity of mass/energy,
    probability range [0, 1], and simple kinematic relations.

    Args:
        text: any text containing quantities, e.g. a draft answer with
              numbers like "450 km/h" or "confidence 1.8".

    Returns:
        JSON string: {"verdict": "PASS|WARN|FAIL", "violations": [...]}
    """
    from phm_lite_check import check_text

    return json.dumps(check_text(text))


INSTRUCTIONS = (
    "You draft short factual answers containing numbers. "
    "Before returning any answer that contains quantities, call "
    "physics_text_check on your draft. If the verdict is FAIL, fix the "
    "flagged claims and re-check. Return only answers whose verdict is "
    "PASS or WARN, and mention the verdict."
)

agent = Agent(
    name="PhysicsGroundedAssistant",
    instructions=INSTRUCTIONS,
    tools=[physics_text_check],
)


async def main() -> None:
    prompt = (
        "A drone descended 450 meters in 30 seconds. State its average "
        "descent speed in km/h and give your confidence that the number is "
        "right, as a probability."
    )
    result = await Runner.run(agent, prompt)
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
