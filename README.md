# 🧪 Prompt Faber Lab — Laboratório de Testes e Avaliação de Prompts

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![Typer](https://img.shields.io/badge/Typer-000000?style=for-the-badge&logo=python)
![LangSmith](https://img.shields.io/badge/LangSmith-FF6B6B?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Teste, compare e melhore seus prompts de forma científica**

[Documentação](https://promptlab.dev) • [PyPI](https://pypi.org/project/promptlab) • [Reportar Bug](https://github.com/c3mprog/promptlab/issues)

</div>

---

## 📌 Sobre o Projeto

**Prompt Faber Lab** é um framework profissional para **testar, versionar e avaliar prompts** de maneira sistemática e reproduzível.

Diferente de testes manuais, o Prompt Faber Lab permite:

- Versionar prompts como código
- Rodar benchmarks em datasets customizados
- Avaliar automaticamente com **LLM-as-Judge**
- Gerar **relatórios executivos** em PDF/HTML
- Comparar múltiplas versões lado a lado com métricas objetivas

**Ideal para**: equipes de AI, pesquisadores, e quem precisa de prompts confiáveis em produção.

---

## ✨ Funcionalidades

- 📝 **Versionamento de Prompts** (YAML + Git-like)
- 🧪 **Test Runner** com datasets em JSON/CSV
- 🤖 **LLM-as-Judge** com critérios customizáveis (Clareza, Factualidade, Utilidade, etc.)
- 📊 **Métricas Híbridas**: exatidão + qualidade + latência
- 📄 **Relatórios Automáticos**: PDF, HTML, Markdown e JSON
- 🔄 **Comparação A/B** entre versões de prompt
- 🖥️ **CLI poderosa** + API Python
- 📈 **Dashboard** interativo (Streamlit)

---

## 🖼️ Screenshots

| CLI em Ação | Relatório PDF Gerado | Dashboard de Comparação |
|-------------|----------------------|-------------------------|
| ![CLI](https://via.placeholder.com/400x250/1a1a2e/ffffff?text=Prompt+Faber+Lab+CLI) | ![PDF](https://via.placeholder.com/400x250/16213e/ffffff?text=Prompt+Faber+Lab+PDF) | ![Dashboard](https://via.placeholder.com/400x250/0f3460/ffffff?text=Prompt+Faber+Lab+Dashboard) |

---

## 🚀 Instalação

```bash
pip install promptlab

# Ou para desenvolvimento
git clone https://github.com/c3mprog/promptlab.git
cd promptlab
pip install -e .
```

---

## 💡 Como Usar

### Via CLI (mais rápido)

```bash
# Avaliar um prompt
promptlab evaluate \
  --prompt prompts/resumo_v3.yaml \
  --dataset datasets/summarization.json \
  --model gpt-4o-mini \
  --output report.pdf

# Comparar duas versões
promptlab compare \
  --prompt-a prompts/v1.yaml \
  --prompt-b prompts/v2.yaml \
  --dataset qa_benchmark.json
```

### Via Python

```python
from promptlab import PromptFaberLab

lab = PromptFaberLab(model="gpt-4o-mini")

results = lab.evaluate(
    prompt_template="Resuma o texto a seguir em 3 frases: {text}",
    test_cases="datasets/summarization.json",
    criteria=["clarity", "conciseness", "factual_accuracy"]
)

print(results.summary())
results.save_report("relatorio.pdf")
```

---

## 📁 Estrutura do Projeto

```
promptlab/
├── promptlab/
│   ├── __init__.py
│   ├── cli.py                    # Interface de linha de comando
│   ├── evaluator.py              # Motor de avaliação
│   ├── prompt_versioner.py       # Versionamento de prompts
│   ├── report_generator.py       # Geração de relatórios PDF/HTML
│   └── metrics/
│       ├── llm_judge.py
│       └── custom_metrics.py
├── datasets/
│   ├── summarization.json
│   ├── code_generation.json
│   └── qa_benchmark.json
├── examples/
│   └── getting_started.py
├── tests/
├── pyproject.toml
└── README.md
```

---

## 📊 Exemplo de Relatório Gerado

```
═══════════════════════════════════════════════════════════════
                 PROMPT FABER LAB - RELATÓRIO DE AVALIAÇÃO
═══════════════════════════════════════════════════════════════

Prompt: resumo_v3.yaml
Dataset: summarization.json (150 casos)
Modelo: gpt-4o-mini

MÉTRICAS GERAIS
───────────────────────────────────────────────────────────────
Clareza ...................... 9.2 / 10    (+1.8 vs v2)
Conciseness .................. 8.7 / 10    (+0.9 vs v2)
Factual Accuracy ............. 94.3%       (+7.2%)
Tempo Médio de Resposta ...... 1.8s        (-0.4s)

COMPARAÇÃO COM VERSÃO ANTERIOR (v2)
───────────────────────────────────────────────────────────────
Melhoria geral: +12.4%
Prompts que melhoraram: 87%
Casos de regressão: 4 (2.7%)

RECOMENDAÇÃO: ✅ APROVADO PARA PRODUÇÃO
```

---

## 🛠️ Tecnologias

- **CLI**: Typer + Rich
- **Avaliação**: LangChain + LangSmith
- **LLM-as-Judge**: GPT-4o / Claude-3.5 / Grok-2
- **Relatórios**: WeasyPrint + Jinja2
- **Dados**: Pandas + Pydantic

---

## 🤝 Contribuindo

1. Fork
2. `git checkout -b feature/nova-metrica`
3. Adicione testes!
4. Abra Pull Request

---

## 📄 Licença

MIT © **Carlos Eduardo Moreno** | [Prompt Faber](https://github.com/prompt-faber)

---

<div align="center">

**Prompt Faber Lab** — Porque prompts bons não são sorte, são ciência.

⭐ Deixe uma estrela se te ajudou!

</div>
