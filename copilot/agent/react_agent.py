import json
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from copilot.config import settings
from copilot.agent.prompts import SYSTEM_PROMPT
from copilot.agent.tools import TOOLS, TOOL_MAP

console = Console()
client = OpenAI(
    api_key=settings.nvidia_api_key,
    base_url=settings.nvidia_base_url
)


def run_react_agent(question: str) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]

    steps = []
    final_answer = ""

    console.print(Panel(f"[bold cyan]Question:[/bold cyan] {question}"))

    for step_num in range(1, settings.max_react_steps + 1):
        console.print(f"\n[bold yellow]Step {step_num}[/bold yellow]")

        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1024
        )

        message = response.choices[0].message

        # No tool call — agent has final answer
        if not message.tool_calls:
            final_answer = message.content or ""
            console.print(Panel(
                f"[bold green]Final Answer:[/bold green]\n{final_answer}",
                border_style="green"
            ))
            break

        # Process tool calls
        messages.append(message)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            console.print(f"  [bold blue]Action:[/bold blue] {tool_name}({tool_args})")

            # Execute tool
            if tool_name in TOOL_MAP:
                observation = TOOL_MAP[tool_name](**tool_args)
            else:
                observation = f"Unknown tool: {tool_name}"

            # Truncate long observations for display
            display_obs = observation[:300] + "..." if len(observation) > 300 else observation
            console.print(f"  [bold magenta]Observe:[/bold magenta] {display_obs}")

            steps.append({
                "step": step_num,
                "action": tool_name,
                "args": tool_args,
                "observation": observation
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": observation
            })

    else:
        final_answer = "Max steps reached without a final answer."
        console.print(f"[bold red]{final_answer}[/bold red]")

    return {
        "question": question,
        "answer": final_answer,
        "steps": steps,
        "step_count": len(steps)
    }