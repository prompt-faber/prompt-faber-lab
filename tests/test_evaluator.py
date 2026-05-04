from __future__ import annotations

from promptlab.evaluator import Evaluator
from promptlab.metrics.llm_judge import HeuristicJudge
from promptlab.model import EchoModel
from promptlab.types import PromptSpec, TestCase


def test_evaluate_echo_model():
    evaluator = Evaluator(model=EchoModel(), judge=HeuristicJudge())
    prompt = PromptSpec(name="t", version="v1", template="Resuma: {text}")
    cases = [TestCase(id="1", input={"text": "abc"}, expected="Resuma: abc")]

    result = evaluator.evaluate(prompt=prompt, dataset_name="d", cases=cases, criteria=["clarity"])
    assert result.summary.prompt_name == "t"
    assert result.summary.accuracy == 100.0
    assert result.cases[0].output == "Resuma: abc"
    assert "clarity" in result.cases[0].scores
