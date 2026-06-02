# Jarvis — Status de Implementação

Documento vivo do que já foi construído e do que ainda falta. Atualizado a
cada avanço. Para a visão geral do projeto, ver [README.md](README.md).

> Última atualização: 2026-06-02

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
| Captura do microfone | `app/audio/recorder.py` | `sounddevice` 16 kHz + VAD por energia **auto-calibrada** (mede ruído de fundo) |
| STT (fala → texto) | `app/audio/recorder.py` | `faster-whisper` local (modelo "small") |
| TTS (texto → fala) | `app/audio/speaker.py` | **OpenAI TTS** (voz "nova") por padrão; `say` do macOS como fallback |
| Hotword "Hey Jarvis" | `app/audio/hotword.py` | **openWakeWord** (grátis, offline, SEM chave) — modelo `hey_jarvis` |
| Confirmação falada | `app/security/confirmations.py` | `VoiceConfirmer`: fala a pergunta e ouve sim/não para ações de risco |
| Loop de voz | `app/main.py` (`modo_voz`) | hotword (ou `--ptt` push-to-talk) → STT → orquestrador → TTS |
| Bandeja (barra de menu) | `app/ui/tray.py` | **experimental**: ícone de estado + "Falar" (rumps); precisa de teste ao vivo |

Estados exibidos no terminal: 🎤 ouvindo · 🧠 pensando · 🔊 falando.
Ativação: por padrão escuta **"Hey Jarvis"**; use `--ptt` para push-to-talk (Enter).

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
- [x] **Captura do microfone ao vivo validada** no Mac do Wilson (transcreveu
      frase falada corretamente; VAD auto-calibrada para o ganho do mic JBL).
- [x] **Hotword "Hey Jarvis"** implementada com openWakeWord (grátis, sem chave).
      → falta só **testar ao vivo** (dizer "Hey Jarvis" e ver se aciona).
- [x] **Confirmação falada** para risco MÉDIO/ALTO (`VoiceConfirmer`).
      → falta **testar ao vivo** o fluxo completo de uma ação MÉDIO por voz.
- [ ] Interrupção (barge-in) — falar por cima da resposta (fase futura).

### Interface visual
- [x] Bandeja de barra de menu (`app/ui/tray.py`, rumps) **implementada**.
      → **experimental: precisa de teste ao vivo** numa sessão gráfica
      (`python -m app.ui.tray`). Hotword contínua na bandeja é passo futuro.
- [ ] Evoluir a bandeja (menu de histórico, toggle de hotword) ou janela GUI.

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
3. **Picovoice — NÃO USAR.** A hotword já funciona de graça com openWakeWord.
   O Picovoice é pago no uso comercial e exige domínio corporativo no
   cadastro — por isso foi descartado. Mantido aqui só como nota histórica.

---

## 🔑 Hotword: Picovoice vs. openWakeWord (resposta à pergunta do Wilson)

> Wilson pediu: "deixe claro que precisa criar a chave do Picovoice e me
> avise se houver alternativa tão boa ou melhor."

**Resultado: o Picovoice foi DESCARTADO (pago no comercial + exige domínio
corporativo no cadastro). A hotword usa openWakeWord — grátis e sem conta.**

| Critério | **openWakeWord** (em uso) | Picovoice Porcupine (descartado) |
|----------|------------------------------|---------------------|
| Conta / chave | **Não precisa** | Precisa (e exige domínio corporativo) |
| Custo | **Grátis** (Apache-2.0) | Pago no uso comercial |
| Offline | Sim | Sim |
| "Hey Jarvis" pronto | Sim (modelo pré-treinado) | Sim |
| Precisão | Muito boa | Excelente (um pouco melhor) |

Se um dia o openWakeWord não satisfizer, estas são as **alternativas grátis**
(todas sem conta/sem custo) para eu avaliar — nenhuma exige Picovoice:

- **Treinar um modelo "Hey Jarvis" customizado no próprio openWakeWord**
  (melhora muito a precisão para a sua voz; grátis).
- **Vosk** — keyword spotting offline, open-source.
- **Detecção via Whisper** já presente (escuta curta + checa se a transcrição
  contém "jarvis"); funciona, porém gasta mais CPU se ficar sempre ligado.

Descartados também: **Snowboy** e **Mycroft Precise** (projetos abandonados).

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
| Hotword | **openWakeWord** ("hey_jarvis") | grátis, sem chave, offline | Picovoice Porcupine (precisa de chave) — ver comparação acima |
| Confirmação (voz) | **falada** (`VoiceConfirmer`) | mãos-livres real; segurança mantida | manter confirmação digitada |
| Interface | **terminal + bandeja rumps** (experimental) | bandeja dá cara de assistente; CLI continua estável | só terminal; janela GUI completa |
| Detecção de fala | **energia/RMS auto-calibrada** | adapta ao ganho do mic | webrtcvad (mais robusto) |
| Modelo STT padrão | **small** | bom equilíbrio qualidade×velocidade PT | tiny/base (pior), medium/large (pesado) |
| Memória | SQLite + perfil no prompt | simples, sem infra | banco vetorial (fase futura) |

### Estado da validação (o que foi testado de fato)
- ✅ STT validado: transcrevi o áudio gerado pelo TTS e recuperei o texto.
- ✅ TTS validado: OpenAI TTS (voz "nova") gera e toca áudio natural; `say`
  segue como fallback offline. (Troca feita após o Wilson achar o `say` ruim.)
- ✅ LLM + ferramentas + guard de risco + auditoria: testados com API real.
- ✅ Captura do microfone ao vivo validada no Mac do Wilson: a função
  `gravar_ate_silencio` + STT transcreveu corretamente uma frase falada.
  VAD passou a auto-calibrar o limiar pelo ruído de fundo (o mic JBL tinha
  ganho baixo e o limiar fixo anterior poderia não detectar a fala).
- ✅ Hotword carrega e roda (openWakeWord, modelo "hey_jarvis"); lógica de
  confirmação por voz testada (sim/não). 33 testes passando.
- ⚠️ **A testar ao vivo (Wilson)**: (1) dizer "Hey Jarvis" e ver se aciona;
  (2) fluxo de confirmação falada numa ação de risco MÉDIO; (3) a bandeja
  `python -m app.ui.tray` numa sessão gráfica.

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

.venv/bin/python -m app.main           # chat por texto
.venv/bin/python -m app.main --voz     # voz com hotword "Hey Jarvis"
.venv/bin/python -m app.main --voz --ptt   # voz com push-to-talk (Enter)
.venv/bin/python -m app.ui.tray        # bandeja na barra de menu (experimental)
.venv/bin/python -m pytest             # testes
```
