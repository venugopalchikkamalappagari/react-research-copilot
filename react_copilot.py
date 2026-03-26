import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from copilot.agent.react_agent import run_react_agent


def main():
    parser = argparse.ArgumentParser(
        description="ReAct Research Copilot — ask questions about the corpus"
    )
    parser.add_argument(
        "--question", "-q",
        type=str,
        required=True,
        help="The question to ask the copilot"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Optional: save result to a JSON file"
    )
    args = parser.parse_args()

    result = run_react_agent(args.question)

    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(result["answer"])
    print(f"\nSteps used: {result['step_count']}")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Result saved to {args.output}")


if __name__ == "__main__":
    main()