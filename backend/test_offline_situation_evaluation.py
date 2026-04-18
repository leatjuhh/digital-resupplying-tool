from pathlib import Path

import pytest

from algorithm_import.config import get_external_algorithm_data_root
from redistribution.offline_evaluation import evaluate_dataset_weeks

EXTERNAL_DATA_ROOT = get_external_algorithm_data_root()


@pytest.mark.skipif(
    not EXTERNAL_DATA_ROOT.exists(),
    reason="Lokale weekdataset voor offline evaluatie ontbreekt.",
)
def test_offline_evaluation_uses_two_local_weeks():
    result = evaluate_dataset_weeks(
        EXTERNAL_DATA_ROOT,
        year=2026,
        weeks=[12, 13],
    )

    assert len(result["weeks"]) == 2
    assert result["article_count"] > 0
    assert result["observed_move_count"] > 0
    assert result["moved_article_count"] > 0
    assert sum(result["situation_counts"].values()) == result["article_count"]
    assert (
        sum(result["moved_article_counts_by_situation"].values())
        == result["moved_article_count"]
    )

    for week_summary in result["weeks"]:
        assert week_summary["per_article"]
        assert week_summary["observed_move_count"] > 0
        assert sum(week_summary["situation_counts"].values()) == week_summary["article_count"]
        assert (
            sum(week_summary["moved_article_counts_by_situation"].values())
            == week_summary["moved_article_count"]
        )
