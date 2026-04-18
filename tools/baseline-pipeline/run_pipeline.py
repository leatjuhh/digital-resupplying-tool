from __future__ import annotations

import argparse
from pathlib import Path

from week_pipeline import run_week_pipeline


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--week", type=int, required=True)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument(
        "--week-dir",
        type=Path,
        default=None,
        help="Pad naar bronmap van de week, bijvoorbeeld Z:\\Herverdeellijsten\\Jaar 2026\\Week 12",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data"),
        help="Rootmap voor pipeline-output",
    )
    args = parser.parse_args()

    week_dir = args.week_dir or Path(rf"Z:\Herverdeellijsten\Jaar {args.year}\Week {args.week}")
    result = run_week_pipeline(
        week=args.week,
        year=args.year,
        week_dir=week_dir,
        output_root=args.output_root,
    )
    print(f"Pipeline voltooid voor week {args.week}: {result['analysis']}")


if __name__ == "__main__":
    main()
