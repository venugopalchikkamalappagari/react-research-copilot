import sys
import glob
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from copilot.evaluation.evaluator import generate_report

runs_dir = "outputs/runs"
baseline_files = sorted(glob.glob(f"{runs_dir}/eval_baseline_*.csv"))
react_files    = sorted(glob.glob(f"{runs_dir}/eval_react_*.csv"))

if baseline_files and react_files:
    report = generate_report(baseline_files[-1], react_files[-1])
    report_path = Path(runs_dir) / "evaluation_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report saved to {report_path}")
    print("\nPreview:")
    print(report[:500])
else:
    print("No CSV files found in outputs/runs/")