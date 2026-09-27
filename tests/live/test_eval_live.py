from pathlib import Path

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator
from google.adk.evaluation.eval_config import get_evaluation_criteria_or_default
from google.adk.evaluation.eval_metrics import LlmAsAJudgeCriterion
from google.adk.evaluation.eval_set import EvalSet

from helpdesk.config import MODEL_ID

EVAL_DIR = Path(__file__).parent.parent / "eval"


@pytest.mark.live
async def test_tools_agent_passes_evalset():
    eval_config = get_evaluation_criteria_or_default(str(EVAL_DIR / "test_config.json"))
    # The judge uses the same model as the agent (MODEL_ID honours HELPDESK_MODEL).
    judge = LlmAsAJudgeCriterion.model_validate(
        eval_config.criteria["final_response_match_v2"].model_dump()
    )
    judge.judge_model_options.judge_model = MODEL_ID
    eval_config.criteria["final_response_match_v2"] = judge

    eval_set = EvalSet.model_validate_json((EVAL_DIR / "nimbus_tools.test.json").read_text())
    await AgentEvaluator.evaluate_eval_set(
        agent_module="agents.m03_tools_solution",
        eval_set=eval_set,
        eval_config=eval_config,
        num_runs=2,
    )
