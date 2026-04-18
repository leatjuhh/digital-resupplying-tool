from __future__ import annotations

import argparse
from pathlib import Path

from model_training import train_and_evaluate_model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    args = parser.parse_args()

    week_dir = args.data_root / str(args.year) / f"week_{args.week}"
    metrics = train_and_evaluate_model(week_dir)
    print(metrics)


if __name__ == "__main__":
    main()
