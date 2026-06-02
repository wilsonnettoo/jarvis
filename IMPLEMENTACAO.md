# Jarvis — Status de Implementação

Documento vivo do que já foi construído e do que ainda falta. Atualizado a
cada avanço. Para a visão geral do projeto, ver [README.md](README.md).

> Última atualização: 2026-06-01

---

## ✅ Concluído

### Etapa 0 — Fundação (núcleo)
Núcleo agnóstico de provedor e de voz, testável por texto. Validado com
chamadas reais de API.

| Componente | Arquivo | O que faz |
|------------|---------|-----------|
| Configuração | `app/config.py` | Lê `.env` via pydantic-settings; modelo/provedor trocável |
| Gateway LLM | `app/agent/llm_gateway.py` | **LiteLLM**: OpenAI/Claude/Gemini/Ollama por 1 interface |
| Registry de ferramentas | `app/tools/registry.py` | Decorator `@tool(risk=...)` + JSON Schema automático |
| Segurança | `app/security/permissions.py`, `confirmations.py` | Classificação de risco + guard de confirmação |
| Memória | `app/agent/memory.py` | SQLite (histórico + auditoria) + perfil estruturado no prompt |
| Persona | `app/agent/prompts.py` | System prompt do Jarvis em PT-BR |
| Orquestrador | `app/agent/orchestrator.py` | Loop async; toda tool passa pelo guard |
| Entrada | `app/main.py` | `python -m app.main` (texto) e `--voz` (voz) |

### Ferramentas (15 no total)

**Sistema / arquivos** (`system_tools.py`, `file_tools.py`)
- BAIXO: `abrir_site`, `abrir_programa`, `abrir_projeto_vscode`,
  `verificar_status_docker`, `listar_processos`,
  `ler_arquivo`, `listar_arquivos`, `pesquisar_arquivo`
- MÉDIO: `criar_arquivo`, `mover_arquivo`

**Técnicas** (`git_tools.py`, `database_tools.py`)
- BAIXO: `git_status`, `git_log`, `branch_atual`
- MÉDIO: `criar_branch`, `criar_commit`, `consultar_postgres` (SELECT-only)

### Voz — MVP (modo `--voz`)
Pipeline modular fala→texto→cérebro→fala, validado de ponta a ponta
(exceto captura do microfone, que precisa de hardware).

| Componente | Arquivo | Tecnologia |
|------------|---------|-----------|
| Captura do microfone | `app/audio/recorder.py` | `sounddevice` 16 kHz + VAD por energia (silêncio) |
| STT (fala → texto) | `app/audio/recorder.py` | `faster-whisper` local (modelo "small") |
| TTS (texto → fala) | `app/audio/speaker.py` | **OpenAI TTS** (voz "nova") por padrão; `say` do macOS como fallback |
| Hotword | `app/audio/hotword.py` | **stub** — hoje é push-to-talk (Enter) |
| Loop de voz | `app/main.py` (`modo_voz`) | push-to-talk → STT → orquestrador → TTS |

Estados exibidos no terminal: 🎤 ouvindo · 🧠 pensando · 🔊 falando.

### Segurança (pilar nº 2)
- Níveis BAIXO / MÉDIO / ALTO / PROIBIDO (`RiskLevel`).
- ALTO sempre confirma; MÉDIO confirma se `JARVIS_REQUIRE_CONFIRMATION=true`.
- Toda execução passa pelo guard do orquestrador e é gravada em `audit_log`.
- `consultar_postgres` recusa qualquer comando de escrita.

### Testes
- 20 testes passando (`pytest`): segurança, registry, file tools, git,
  postgres, áudio (TTS render + STT vazio).

---

## 🚧 Próximo

### Voz — completar
- [ ] **Testar captura do microfone ao vivo** (só funciona no Mac do Wilson;
      pode exigir permissão de Microfone no macOS na 1ª vez).
- [ ] Hotword "Jarvis" (Picovoice) — precisa de `PICOVOICE_ACCESS_KEY`.
- [ ] Confirmações **faladas** para risco MÉDIO/ALTO (hoje a confirmação no
      modo voz ainda é digitada no terminal).
- [ ] Interrupção (barge-in) — falar por cima da resposta.

### Interface visual
- [ ] Evoluir do terminal para **barra de menu (macOS, rumps)** com ícone
      de estado, depois opcionalmente janela GUI.

---

## 📋 Backlog (fases futuras)

- [ ] **Ferramentas MV Travel**: roteiros, propostas, posts, checklists
- [ ] **Navegador** (`browser_tools.py`): Playwright, coleta, formulários
- [ ] **Produtividade**: calendário, e-mail, lembretes, gerar PDF
- [ ] **Git destrutivo / DB escrita**: ferramentas de risco ALTO
- [ ] **Memória avançada**: banco vetorial para busca semântica
- [ ] **Modo Realtime** (OpenAI) para voz de baixa latência
- [ ] **Push para o GitHub** (atualmente vários commits à frente do `origin`)

---

## ⚠️ Pendências de decisão (dependem do Wilson)

1. **Reset de tokens**: não detecto sozinho nem sei o horário do reset —
   quando o Claude Code avisar, passar o horário para agendar a retomada.
2. **Push para o GitHub**: precisa de autorização (ação externa).
3. **Chave Picovoice**: criar grátis em console.picovoice.ai para liberar a
   hotword "Jarvis".

---

## 🧭 Review — decisões tomadas (e alternativas)

Registro das escolhas de arquitetura, com o que foi descartado e por quê.
(Wilson pediu que eu decida e deixe anotado; nenhuma destas exigiu pergunta.)

| Tema | Escolhido | Por quê | Outras opções consideradas |
|------|-----------|---------|----------------------------|
| Provedor de LLM | **LiteLLM** (gateway único) | troca por config, suporta os 4 | SDKs próprios por provedor |
| Estratégia de voz | **Pipeline modular** (STT→LLM→TTS) | funciona com qualquer LLM | Realtime OpenAI (só OpenAI) |
| Ordem de build | fundação texto → voz | validar barato antes do áudio | voz primeiro (mais fricção) |
| Interface (voz) | **Terminal rico** | zero deps, voz já funcionando | barra de menu (rumps), janela GUI |
| Ativação | **Push-to-talk** (Enter) | sem chave externa; destrava já | hotword Porcupine (precisa de chave) |
| STT | **faster-whisper local** | grátis, offline, privado | OpenAI Whisper API (custo, envia áudio) |
| TTS | **OpenAI TTS** (voz "nova") | voz natural; `say` era robótico (feedback do Wilson) | macOS `say` (fallback offline), ElevenLabs, Piper |
| Detecção de fala | **energia/RMS** | menos dependências | webrtcvad (mais robusto) |
| Modelo STT padrão | **small** | bom equilíbrio qualidade×velocidade PT | tiny/base (pior), medium/large (pesado) |
| Memória | SQLite + perfil no prompt | simples, sem infra | banco vetorial (fase futura) |

### Estado da validação (o que foi testado de fato)
- ✅ STT validado: transcrevi o áudio gerado pelo TTS e recuperei o texto.
- ✅ TTS validado: OpenAI TTS (voz "nova") gera e toca áudio natural; `say`
  segue como fallback offline. (Troca feita após o Wilson achar o `say` ruim.)
- ✅ LLM + ferramentas + guard de risco + auditoria: testados com API real.
- ⚠️ **Não testado aqui**: captura do microfone ao vivo (ambiente sem mic).
  É o único ponto a confirmar no Mac do Wilson.

### Riscos/limitações conhecidos
- Python 3.14 é novo; as libs de voz têm wheel e funcionam, mas fique atento
  a incompatibilidades em libs futuras.
- VAD por energia pode cortar cedo em ambiente barulhento — ajustar `limiar`
  e `silencio_seg` em `recorder.py` se necessário.
- Latência do modo voz: STT local "small" em CPU tem alguns segundos de
  atraso; cair para "base" acelera, ou usar Realtime/API no futuro.

---

## Como rodar (estado atual)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env             # preencher OPENAI_API_KEY (ou outro provedor)

.venv/bin/python -m app.main         # chat por texto
.venv/bin/python -m app.main --voz   # conversa por voz (Enter para falar)
.venv/bin/python -m pytest           # testes
```
