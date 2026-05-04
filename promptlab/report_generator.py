from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, select_autoescape

from promptlab.types import EvaluationResult


@dataclass(frozen=True)
class ReportGenerator:
    def save(self, result: EvaluationResult, output_path: Path) -> Path:
        suffix = output_path.suffix.lower().lstrip(".")
        if suffix == "json":
            output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
            return output_path
        if suffix == "html":
            output_path.write_text(_render_html(result), encoding="utf-8")
            return output_path
        if suffix in {"md", "markdown"}:
            output_path.write_text(_render_md(result), encoding="utf-8")
            return output_path
        if suffix == "pdf":
            return _render_pdf(result, output_path)
        raise ValueError("Formato de relatório inválido. Use: .json, .html, .md ou .pdf")


def _render_html(result: EvaluationResult) -> str:
    env = Environment(autoescape=select_autoescape(enabled_extensions=("html",)))
    template = env.from_string(_HTML_TEMPLATE)
    return template.render(result=result.model_dump())


def _render_md(result: EvaluationResult) -> str:
    s = result.summary
    lines: list[str] = []
    lines.append("# Prompt Faber Lab — Relatório de Avaliação")
    lines.append("")
    lines.append(f"- Prompt: {s.prompt_name} ({s.prompt_version})")
    lines.append(f"- Dataset: {s.dataset_name} ({len(result.cases)} casos)")
    lines.append(f"- Modelo: {s.model}")
    lines.append(f"- Critérios: {', '.join(s.criteria)}")
    lines.append(f"- Latência média: {s.avg_latency_ms:.1f}ms")
    lines.append(f"- Score médio: {s.avg_score:.2f}/10")
    if s.accuracy is not None:
        lines.append(f"- Accuracy: {s.accuracy:.1f}%")
    lines.append("")
    lines.append("## Casos")
    lines.append("")
    for c in result.cases[:50]:
        lines.append(f"### {c.case_id or '(sem id)'}")
        lines.append("")
        lines.append("**Output**")
        lines.append("")
        lines.append("```")
        lines.append(c.output)
        lines.append("```")
        lines.append("")
        lines.append(f"- Latência: {c.latency_ms:.1f}ms")
        if c.passed is not None:
            lines.append(f"- Passou: {'sim' if c.passed else 'não'}")
        lines.append(f"- Scores: {json.dumps(c.scores, ensure_ascii=False)}")
        lines.append("")
    if len(result.cases) > 50:
        lines.append(f"_Exibindo 50/{len(result.cases)} casos._")
    lines.append("")
    return "\n".join(lines)


def _render_pdf(result: EvaluationResult, output_path: Path) -> Path:
    try:
        from weasyprint import HTML  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "Dependência opcional não instalada. Instale com: pip install 'promptlab[reports]'"
        ) from exc
    html = _render_html(result)
    HTML(string=html).write_pdf(str(output_path))
    return output_path


_HTML_TEMPLATE = """
<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Prompt Faber Lab — Relatório</title>
    <style>
      body { font-family: Arial, sans-serif; padding: 24px; color: #111; }
      .meta { margin-bottom: 16px; }
      .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
      .card { border: 1px solid #ddd; border-radius: 8px; padding: 12px; }
      pre { white-space: pre-wrap; word-break: break-word; }
      .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; background: #eef; }
    </style>
  </head>
  <body>
    <h1>Prompt Faber Lab — Relatório de Avaliação</h1>
    <div class="meta">
      <div><span class="badge">Prompt</span> {{ result.summary.prompt_name }} ({{ result.summary.prompt_version }})</div>
      <div><span class="badge">Dataset</span> {{ result.summary.dataset_name }} ({{ result.cases | length }} casos)</div>
      <div><span class="badge">Modelo</span> {{ result.summary.model }}</div>
      <div><span class="badge">Critérios</span> {{ result.summary.criteria | join(', ') }}</div>
    </div>

    <div class="grid">
      <div class="card">
        <h3>Métricas gerais</h3>
        <div>Latência média: <b>{{ '%.1f'|format(result.summary.avg_latency_ms) }}ms</b></div>
        <div>Score médio: <b>{{ '%.2f'|format(result.summary.avg_score) }}/10</b></div>
        {% if result.summary.accuracy is not none %}
        <div>Accuracy: <b>{{ '%.1f'|format(result.summary.accuracy) }}%</b></div>
        {% endif %}
      </div>
      <div class="card">
        <h3>Recomendação</h3>
        {% if result.summary.avg_score >= 8.0 %}
          <div><b>✅ APROVADO PARA PRODUÇÃO</b></div>
        {% else %}
          <div><b>⚠️ REVISAR PROMPT</b></div>
        {% endif %}
      </div>
    </div>

    <h2 style="margin-top: 24px">Casos</h2>
    {% for c in result.cases[:50] %}
      <div class="card" style="margin-bottom: 12px">
        <div><b>{{ c.case_id or '(sem id)' }}</b> — {{ '%.1f'|format(c.latency_ms) }}ms</div>
        <div>Scores: {{ c.scores }}</div>
        <pre>{{ c.output }}</pre>
      </div>
    {% endfor %}
    {% if (result.cases | length) > 50 %}
      <div><i>Exibindo 50/{{ result.cases | length }} casos.</i></div>
    {% endif %}
  </body>
</html>
"""
