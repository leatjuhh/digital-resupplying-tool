from __future__ import annotations

import argparse
from pathlib import Path

from training_data import generate_training_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--data-root", type=Path, default=Path("data"))
    args = parser.parse_args()

    week_dir = args.data_root / str(args.year) / f"week_{args.week}"
    result = generate_training_data(week_dir, year=args.year, week=args.week)
    print(result)


if __name__ == "__main__":
    main()
