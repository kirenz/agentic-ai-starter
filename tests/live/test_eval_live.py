from pathlib import Path

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

EVAL_DIR = Path(__file__).parent.parent / "eval"


@pytest.mark.live
async def test_tools_agent_passes_evalset():
    await AgentEvaluator.evaluate(
        agent_module="agents.m03_tools_solution",
        eval_dataset_file_path_or_dir=str(EVAL_DIR / "nimbus_tools.test.json"),
        num_runs=2,
    )
