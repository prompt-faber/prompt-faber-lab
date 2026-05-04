from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import print

from promptlab.lab import PromptFaberLab

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command("evaluate")
def evaluate_cmd(
    prompt: Path = typer.Option(..., "--prompt", exists=True, readable=True),
    dataset: Path = typer.Option(..., "--dataset", exists=True, readable=True),
    model: str = typer.Option("echo", "--model"),
    output: Path = typer.Option(Path("report.json"), "--output"),
    criteria: list[str] = typer.Option(
        ["clarity", "conciseness", "factual_accuracy"],
        "--criteria",
        help="Pode ser repetido: --criteria clarity --criteria conciseness",
    ),
) -> None:
    lab = PromptFaberLab.create(model=model)
    result = lab.evaluate(prompt_file=prompt, test_cases=dataset, criteria=criteria)
    out = lab.save_report(result, output)
    print(f"[green]OK[/green] Relatório salvo em: {out}")


@app.command("compare")
def compare_cmd(
    prompt_a: Path = typer.Option(..., "--prompt-a", exists=True, readable=True),
    prompt_b: Path = typer.Option(..., "--prompt-b", exists=True, readable=True),
    dataset: Path = typer.Option(..., "--dataset", exists=True, readable=True),
    model: str = typer.Option("echo", "--model"),
    output: Path = typer.Option(Path("comparison.json"), "--output"),
) -> None:
    lab = PromptFaberLab.create(model=model)
    a = lab.evaluate(prompt_file=prompt_a, test_cases=dataset, criteria=["clarity", "conciseness"])
    b = lab.evaluate(prompt_file=prompt_b, test_cases=dataset, criteria=["clarity", "conciseness"])
    comparison = lab.compare(a, b)
    output.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]OK[/green] Comparação salva em: {output}")
