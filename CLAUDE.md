# CLAUDE.md — Contexto do projeto Jarvis

Arquivo de contexto carregado a cada sessão. Leia antes de agir. Para o
status detalhado, ver [IMPLEMENTACAO.md](IMPLEMENTACAO.md); para a visão
futura multiagente, [jarvis_agentic_core.md](jarvis_agentic_core.md).

## O que é
Assistente pessoal de voz do Wilson (PT-BR), em **Python 3.14 / macOS**.
Acorda por hotword, ouve, pensa (LLM), executa ferramentas com segurança e
responde por voz. Núcleo agnóstico de provedor e de voz.

## Como rodar / testar
```bash
.venv/bin/python -m app.main            # chat por texto
.venv/bin/python -m app.main --voz      # voz (hotword "Hey Jarvis")
.venv/bin/python -m app.main --voz --ptt  # voz com push-to-talk (Enter)
.venv/bin/python -m app.ui.tray         # bandeja na barra de menu (experimental)
.venv/bin/python -m pytest              # testes (33 passando)
```
Encerrar o Jarvis: dizer/digitar **"vai dormir"**.

## Arquitetura (decisões travadas)
- **LLM via LiteLLM** (`app/agent/llm_gateway.py`) — troca de provedor por
  `JARVIS_MODEL` no `.env` (OpenAI/Claude/Gemini/Ollama).
- **Ferramentas** (`app/tools/`) — decorador `@tool(risk=...)` em
  `registry.py` gera o JSON Schema automático. 15 ferramentas hoje.
- **Segurança** (`app/security/`) — `RiskLevel` BAIXO/MÉDIO/ALTO/PROIBIDO;
  guard obrigatório no orquestrador; tudo gravado em `audit_log`. Nenhuma
  ferramenta roda fora do guard.
- **Memória** (`app/agent/memory.py`) — SQLite (histórico + auditoria) +
  perfil estruturado injetado no system prompt. Sem vetores no MVP.
- **Orquestrador** (`app/agent/orchestrator.py`) — loop async de tool-calling.
- **Voz** — pipeline modular: hotword **openWakeWord** ("hey_jarvis", grátis,
  sem chave) → STT **faster-whisper** (local) → LLM → TTS. Confirmações de
  risco são **faladas** no modo voz (`VoiceConfirmer`).
- **TTS atual** = **ElevenLabs**, voz **clonada do Tony Stark** (engine
  `elevenlabs`). Alternativas no `Speaker`: `openai` (gpt-4o-mini-tts, rápido),
  `xtts` (clone local, ficou robótico/lento), `say` (fallback macOS).

## Convenções
- Código e comentários em **português do Brasil**.
- Mensagens de commit em PT-BR, com `Co-Authored-By: Claude...`.
- **Sempre atualizar `IMPLEMENTACAO.md`** a cada avanço (decisões +
  alternativas + o que falta).
- Adicionar capacidade = escrever função decorada com `@tool` no módulo certo
  de `app/tools/` e importá-la em `app/main.py` (o import registra a tool).

## Preferências do Wilson (importante)
- Quer que o Claude **atue como arquiteto, decida e registre** as escolhas;
  **não perguntar demais** — decidir com bom senso e anotar no IMPLEMENTACAO.md.
- Responder sempre em PT-BR, objetivo e prático.
- Confirmar antes de ações sensíveis (mas a camada de segurança já cuida disso).

## Estado atual e o que falta
- ✅ Feito: cérebro multi-LLM, 15 ferramentas (arquivo + técnicas),
  segurança/auditoria, memória, **voz completa** (hotword + STT + TTS clonado).
- ❌ **Parte WEB = 0%** (`browser_tools.py` vazio; Playwright nem instalado).
- ❌ Backlog: ferramentas MV Travel, produtividade, ações de risco ALTO,
  barge-in, memória vetorial, visão Jarvis Agentic Core.

## Avisos / gotchas
- **Segredos**: ficam só no `.env` (gitignored). Mídia (`.mp3/.mp4/.wav`)
  também é ignorada. NÃO commitar nada disso.
- **Não há push para o GitHub ainda** — vários commits locais à frente do
  `origin`; só dar push com autorização explícita do Wilson.
- **transformers fixado <5** (XTTS quebra com 5.x). **PyAV recompilado**
  contra o ffmpeg do sistema (evita aviso de classe duplicada no macOS).
- **Chave ElevenLabs foi exposta no chat** uma vez → recomendado regenerar.
- Voz do Tony Stark/JARVIS é de filme: uso **pessoal** ok; **comercial**
  (MV Travel) precisa de voz própria/licenciada.

## Trocar o modelo do Claude Code
Use `/model` e escolha **Opus 4.8** (mais capaz) ou **Sonnet 4.6** (mais
rápido/barato). Este `CLAUDE.md` garante que o novo modelo já inicie com
contexto. (Para mudar o cérebro do *Jarvis*, edite `JARVIS_MODEL` no `.env`.)
