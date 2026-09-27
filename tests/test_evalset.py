import json
from pathlib import Path

from google.adk.evaluation.eval_set import EvalSet

EVAL_DIR = Path(__file__).parent / "eval"


def test_evalset_matches_adk_schema():
    data = json.loads((EVAL_DIR / "nimbus_tools.test.json").read_text())
    eval_set = EvalSet.model_validate(data)
    assert len(eval_set.eval_cases) == 3
    tool_names = [
        tu.name
        for case in eval_set.eval_cases
        for inv in case.conversation
        for tu in inv.intermediate_data.tool_uses
    ]
    assert tool_names == ["get_order_status", "search_manual", "get_order_status"]


def test_config_defines_criteria():
    config = json.loads((EVAL_DIR / "test_config.json").read_text())
    assert set(config["criteria"]) == {"tool_trajectory_avg_score", "final_response_match_v2"}
    judge = config["criteria"]["final_response_match_v2"]
    assert judge["threshold"] == 0.8
    assert judge["judge_model_options"]["num_samples"] == 3


def test_judge_model_mirrors_default_model_id():
    # The adk eval CLI reads the JSON as is; the live pytest sets MODEL_ID at runtime.
    from helpdesk import config as helpdesk_config

    config = json.loads((EVAL_DIR / "test_config.json").read_text())
    judge_model = config["criteria"]["final_response_match_v2"]["judge_model_options"]["judge_model"]
    assert judge_model == helpdesk_config.DEFAULT_MODEL_ID


def test_trajectory_criterion_compares_tool_names_only():
    from google.adk.evaluation.eval_config import EvalConfig
    from google.adk.evaluation.eval_metrics import EvalMetric, ToolTrajectoryCriterion
    from google.adk.evaluation.trajectory_evaluator import TrajectoryEvaluator

    config = EvalConfig.model_validate_json((EVAL_DIR / "test_config.json").read_text())
    evaluator = TrajectoryEvaluator(
        eval_metric=EvalMetric(
            metric_name="tool_trajectory_avg_score",
            criterion=config.criteria["tool_trajectory_avg_score"],
        )
    )
    # search_manual queries are free text, so only tool names and order count.
    assert evaluator._match_type == ToolTrajectoryCriterion.MatchType.EXACT
    assert evaluator._ignore_args is True
    assert evaluator._threshold == 1.0
