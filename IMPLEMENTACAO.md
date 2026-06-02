# Jarvis — Status de Implementação

Documento vivo do que já foi construído e do que ainda falta. Atualizado a
cada avanço. Para a visão geral do projeto, ver [README.md](README.md).

> Última atualização: 2026-06-01

---

## ✅ Concluído

### Etapa 0 — Fundação (núcleo)
Núcleo agnóstico de provedor e de voz, testável por texto. Tudo isto roda
sem áudio e foi validado com chamadas reais de API.

| Componente | Arquivo | O que faz |
|------------|---------|-----------|
| Configuração | `app/config.py` | Lê `.env` via pydantic-settings; modelo/provedor trocável |
| Gateway LLM | `app/agent/llm_gateway.py` | **LiteLLM**: OpenAI/Claude/Gemini/Ollama por 1 interface |
| Registry de ferramentas | `app/tools/registry.py` | Decorator `@tool(risk=...)` + JSON Schema automático |
| Segurança | `app/security/permissions.py`, `confirmations.py` | Classificação de risco + guard de confirmação |
| Memória | `app/agent/memory.py` | SQLite (histórico + auditoria) + perfil estruturado no prompt |
| Persona | `app/agent/prompts.py` | System prompt do Jarvis em PT-BR |
| Orquestrador | `app/agent/orchestrator.py` | Loop async; toda tool passa pelo guard |
| Entrada | `app/main.py` | REPL de terminal (`python -m app.main`) |

### Ferramentas (15 no total)

**Sistema / arquivos** (`system_tools.py`, `file_tools.py`)
- BAIXO: `abrir_site`, `abrir_programa`, `abrir_projeto_vscode`,
  `verificar_status_docker`, `listar_processos`,
  `ler_arquivo`, `listar_arquivos`, `pesquisar_arquivo`
- MÉDIO: `criar_arquivo`, `mover_arquivo`

**Técnicas** (`git_tools.py`, `database_tools.py`)
- BAIXO: `git_status`, `git_log`, `branch_atual`
- MÉDIO: `criar_branch`, `criar_commit`, `consultar_postgres` (SELECT-only)

### Segurança (pilar nº 2)
- Níveis BAIXO / MÉDIO / ALTO / PROIBIDO (`RiskLevel`).
- ALTO sempre confirma; MÉDIO confirma se `JARVIS_REQUIRE_CONFIRMATION=true`.
- Toda execução passa pelo guard do orquestrador e é gravada em `audit_log`.
- `consultar_postgres` recusa qualquer comando de escrita.

### Testes
- 17 testes passando (`pytest`): segurança, registry, file tools, git, postgres.

### Decisões de arquitetura (ADR)
- Multi-LLM via **LiteLLM** (troca por `JARVIS_MODEL` no `.env`).
- Voz será **pipeline modular** (STT→LLM→TTS) — funciona com qualquer
  provedor; Realtime (OpenAI) fica como modo turbo opcional.
- Núcleo **async-first** para suportar interrupção (barge-in) na voz.
- Memória sem vetores no MVP (perfil injetado no prompt).

---

## 🚧 Em andamento / Próximo

### Voz (PRIORIDADE ATUAL — fase escolhida pelo Wilson)
Objetivo: Jarvis acorda por palavra-chave, ouve, pensa e responde falando.

- [ ] Captura de áudio do microfone (`audio/recorder.py`)
- [ ] STT — fala → texto (Whisper API ou `faster-whisper` local)
- [ ] TTS — texto → fala (OpenAI TTS ou alternativa)
- [ ] Hotword "Jarvis" (`audio/hotword.py`, Picovoice Porcupine)
- [ ] Loop de voz integrado ao orquestrador existente
- [ ] Confirmações faladas para ações de risco MÉDIO/ALTO

### Interface visual
- [ ] Decidir formato: ícone na barra de menu (tray) vs janela GUI vs TUI rica
- [ ] Indicador de estado (ouvindo / pensando / falando)

---

## 📋 Backlog (fases futuras)

- [ ] **Ferramentas MV Travel**: roteiros, propostas, posts, checklists
- [ ] **Navegador** (`browser_tools.py`): Playwright, coleta de dados, formulários
- [ ] **Produtividade**: calendário, e-mail, lembretes, gerar PDF
- [ ] **Git destrutivo / DB escrita**: ferramentas de risco ALTO com confirmação
- [ ] **Memória avançada**: banco vetorial para busca semântica
- [ ] **Modo Realtime** (OpenAI) para voz de baixa latência
- [ ] **Push para o GitHub** (atualmente N commits à frente do `origin`)

---

## ⚠️ Pendências de decisão (dependem do Wilson)

1. **Reset de tokens**: não consigo detectar sozinho nem saber o horário do
   reset — quando o Claude Code avisar, passar o horário para agendar a retomada.
2. **Push para o GitHub**: precisa de autorização (ação externa).
3. **Provedores de STT/TTS**: definir API (OpenAI) vs local (Whisper/Piper).

---

## Como rodar (estado atual)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env          # preencher uma chave de LLM (ex.: OPENAI_API_KEY)
.venv/bin/python -m app.main  # REPL de texto
.venv/bin/python -m pytest    # testes
```
