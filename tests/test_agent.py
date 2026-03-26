from copilot.agent.react_agent import run_react_agent


def test_agent_returns_answer():
    result = run_react_agent("What is a North Star metric?")
    assert "answer" in result
    assert len(result["answer"]) > 0
    assert "step_count" in result
    assert result["step_count"] >= 1


def test_agent_returns_steps():
    result = run_react_agent("What is variance analysis?")
    assert "steps" in result
    assert isinstance(result["steps"], list)