"""Simulate a group sharing one API key: N parallel sessions, R requests each.

Usage: uv run python -m scripts.load_test --sessions 6 --requests 5
"""

import argparse
import asyncio
import time

from google.adk.runners import InMemoryRunner

from agents.m03_tools_solution.agent import root_agent

PROMPTS = ["Where is my order NH-1002?", "How do I reset the wifi?", "Can I return my hub after 20 days?"]


async def session_worker(runner: InMemoryRunner, idx: int, requests: int, stats: dict) -> None:
    for r in range(requests):
        start = time.perf_counter()
        try:
            await runner.run_debug(PROMPTS[r % len(PROMPTS)], user_id=f"u{idx}", session_id=f"s{idx}", quiet=True)
            stats["ok"] += 1
            stats["latency"].append(time.perf_counter() - start)
        except Exception as exc:  # report every failure type, incl. 429 after retries
            stats["errors"].append(type(exc).__name__ + ": " + str(exc)[:120])


async def main(sessions: int, requests: int) -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="load_test")
    stats = {"ok": 0, "errors": [], "latency": []}
    await asyncio.gather(*(session_worker(runner, i, requests, stats) for i in range(sessions)))
    lat = sorted(stats["latency"])
    print(f"ok={stats['ok']} errors={len(stats['errors'])}")
    if lat:
        print(f"latency median={lat[len(lat) // 2]:.1f}s max={lat[-1]:.1f}s")
    for err in stats["errors"][:10]:
        print("  ", err)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", type=int, default=6)
    parser.add_argument("--requests", type=int, default=5)
    args = parser.parse_args()
    asyncio.run(main(args.sessions, args.requests))
