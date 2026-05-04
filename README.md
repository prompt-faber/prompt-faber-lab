<div align="center">
  <img src="assets/images/logo.png" alt="Prompt Faber Lab" width="420" />
</div>

<br>

# 🧪 Prompt Faber Lab — Laboratório de Testes e Avaliação de Prompts

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![Typer](https://img.shields.io/badge/Typer-000000?style=for-the-badge&logo=python)
![LangSmith](https://img.shields.io/badge/LangSmith-FF6B6B?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Teste, compare e melhore seus prompts de forma científica**

[Documentação](https://promptfaber.com) • [GitHub](https://github.com/prompt-faber/prompt-faber-lab) • [Reportar Bug](https://github.com/prompt-faber/prompt-faber-lab/issues)

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

**Ideal para**: equipes de AI, pesquisadores, Prompt Engineers e quem precisa de prompts confiáveis em produção.

---

## ✨ Funcionalidades

- 📝 **Versionamento de Prompts** (YAML + Git-like)
- 🧪 **Test Runner** com datasets em JSON/CSV
- 🤖 **LLM-as-Judge** com critérios customizáveis
- 📊 **Métricas Híbridas**: exatidão + qualidade + latência
- 📄 **Relatórios Automáticos**: PDF, HTML, Markdown e JSON
- 🔄 **Comparação A/B** entre versões de prompt
- 🖥️ **CLI poderosa** + API Python
- 📈 **Dashboard** interativo (Streamlit)

---

## 🖼️ Screenshots

*(Em breve — adicione suas imagens aqui)*

---

## 🚀 Instalação

```bash
pip install promptlab

# Ou para desenvolvimento
git clone https://github.com/prompt-faber/prompt-faber-lab.git
cd prompt-faber-lab
pip install -e .

💡 Como Usar
Via CLI (mais rápido)
Bash# Avaliar um prompt
promptlab evaluate \
  --prompt prompts/resumo_v3.yaml \
  --dataset datasets/summarization.json \
  --model gpt-4o-mini \
  --output report.pdftemp.sh: line 2: promptlab: command not found

Via Python
Pythonfrom promptlab import PromptFaberLab

lab = PromptFaberLab(model="gpt-4o-mini")

results = lab.evaluate(
    prompt_template="Resuma o texto a seguir em 3 frases: {text}",
    test_cases="datasets/summarization.json",
    criteria=["clarity", "conciseness", "factual_accuracy"]
)

print(results.summary())
results.save_report("relatorio.pdf")

📁 Estrutura do Projeto
textprompt-faber-lab/
├── promptlab/
│   ├── cli.py
│   ├── evaluator.py
│   ├── prompt_versioner.py
│   └── ...
├── assets/images/logo.png
├── datasets/
├── examples/
├── tests/
├── pyproject.toml
└── README.md

📄 Licença
MIT © Eduardo Moreno | Prompt Faber


Prompt Faber Lab — Porque prompts bons não são sorte, são ciência.
⭐ Se este projeto te ajudar, não esqueça de dar uma estrela!