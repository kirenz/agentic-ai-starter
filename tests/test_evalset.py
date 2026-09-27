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
    assert set(config["criteria"]) == {"tool_trajectory_avg_score", "response_match_score"}


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
