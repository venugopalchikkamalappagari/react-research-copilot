import sys
import csv
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from copilot.evaluation.evaluator import evaluate, save_results


def load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    # Run baseline
    print("=" * 60)
    print("BASELINE EVALUATION (no tools)")
    print("=" * 60)
    baseline_results = evaluate(mode="baseline")
    save_results(baseline_results, "baseline")

    # Run ReAct
    print("\n" + "=" * 60)
    print("REACT EVALUATION (with tools)")
    print("=" * 60)
    react_results = evaluate(mode="react")
    save_results(react_results, "react")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    baseline_gp = sum(float(r["grounded_precision"]) for r in baseline_results) / len(baseline_results)
    react_gp = sum(float(r["grounded_precision"]) for r in react_results) / len(react_results)

    print(f"Baseline grounded precision:  {baseline_gp:.2f}")
    print(f"ReAct    grounded precision:  {react_gp:.2f}")
    print(f"Improvement:                  +{react_gp - baseline_gp:.2f}")


if __name__ == "__main__":
    main()
    # Generate written report
    from copilot.evaluation.evaluator import generate_report
    from pathlib import Path
    import glob

    runs_dir = "outputs/runs"
    baseline_files = sorted(glob.glob(f"{runs_dir}/eval_baseline_*.csv"))
    react_files    = sorted(glob.glob(f"{runs_dir}/eval_react_*.csv"))

    if baseline_files and react_files:
        report = generate_report(baseline_files[-1], react_files[-1])
        report_path = Path(runs_dir) / "evaluation_report.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"\nEvaluation report saved to {report_path}")