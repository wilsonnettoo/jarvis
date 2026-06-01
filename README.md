# Jarvis — Assistente Virtual Pessoal

Projeto para criação de um assistente virtual próprio, inspirado no Jarvis, com ativação por voz, conversação natural, memória personalizada, integração com ferramentas locais e capacidade de executar tarefas no computador com segurança.

Repositório GitHub:

```text
https://github.com/wilsonnettoo/jarvis.git
```

---

## 1. Objetivo do projeto

Criar um assistente virtual pessoal capaz de:

- acordar por comando de voz, como “Jarvis”;
- ouvir comandos falados;
- responder por voz em português do Brasil;
- executar ações no computador;
- consultar e manipular arquivos locais;
- ajudar no trabalho técnico com PostgreSQL, Docker e VS Code;
- apoiar a operação da agência MV Travel;
- criar roteiros, propostas, posts e automações para viagens de experiência;
- manter memória personalizada sobre preferências, contexto profissional e ambiente técnico;
- pedir confirmação antes de ações sensíveis.

O objetivo final não é apenas criar um chatbot com voz, mas um assistente operacional capaz de ajudar em tarefas reais do dia a dia.

---

## 2. Visão geral da arquitetura

A arquitetura inicial do Jarvis deve seguir esta lógica:

```text
Hotword local
   ↓
Captura de áudio / VAD / interrupção
   ↓
Realtime Voice ou STT
   ↓
Orquestrador do agente
   ↓
Memória + Ferramentas + Permissões
   ↓
Ação no computador / resposta falada
   ↓
Logs, segurança e confirmação humana
```

---

## 3. Componentes principais

### 3.1 Ativação por voz — Hotword

O assistente deve ficar escutando localmente e acordar apenas quando ouvir uma palavra-chave, como:

```text
Jarvis
```

Biblioteca sugerida:

```text
Picovoice Porcupine
```

Função desta camada:

- detectar a palavra de ativação;
- evitar que o assistente fique processando áudio o tempo inteiro;
- iniciar a gravação do comando após o hotword.

---

### 3.2 Captura de áudio

Após detectar o hotword, o sistema deve capturar a fala do usuário.

Recursos desejados:

- gravação do microfone;
- detecção de silêncio;
- cancelamento de ruído, se possível;
- suporte a interrupção;
- envio do áudio para a camada de inteligência.

Bibliotecas possíveis:

```text
sounddevice
pyaudio
webrtcvad
```

---

### 3.3 Transcrição de voz — STT

STT significa Speech-to-Text, ou seja, transformar fala em texto.

Opções:

```text
OpenAI Whisper API
whisper.cpp local
OpenAI Realtime API
```

Para a primeira versão, a melhor opção pode ser usar uma API realtime de voz, reduzindo a necessidade de separar manualmente STT, LLM e TTS.

Para uma versão offline ou híbrida, pode-se usar:

```text
whisper.cpp
```

---

### 3.4 Cérebro da IA

O cérebro do Jarvis recebe o comando do usuário e decide o que fazer.

Ele pode:

- responder uma pergunta;
- pedir mais contexto;
- chamar uma ferramenta;
- consultar memória;
- executar uma ação;
- pedir confirmação antes de executar algo sensível.

Modelos possíveis:

```text
OpenAI GPT
OpenAI Realtime API
OpenAI Agents SDK
Gemini
Claude
Ollama local
```

Para o MVP, a sugestão principal é:

```text
OpenAI Realtime API + ferramentas locais em Python
```

---

### 3.5 Voz de resposta — TTS

TTS significa Text-to-Speech, ou seja, transformar texto em voz.

O Jarvis precisa responder falando com o usuário.

Opções:

```text
OpenAI TTS
OpenAI Realtime API
ElevenLabs
Piper TTS local
Coqui TTS
```

Para a primeira versão, a melhor alternativa é usar uma camada realtime que já entregue conversa por voz.

---

## 4. Memória personalizada

O Jarvis precisa lembrar informações importantes sobre o usuário, o ambiente de trabalho e a agência.

### 4.1 Memória pessoal

```text
- prefere português do Brasil
- gosta de comandos práticos
- prefere respostas objetivas e com passo a passo
- quer confirmação antes de ações sensíveis
```

### 4.2 Memória profissional

```text
- trabalha com agência de viagens
- sua agência é MV Travel
- quer foco em viagens de experiência
- trabalha com roteiros personalizados
- quer digitalizar atendimento e operação
- quer apoio em marketing, propostas e automações
```

### 4.3 Memória técnica

```text
- usa MacBook Pro M4 Pro
- usa PostgreSQL
- usa Docker
- usa VS Code
- trabalha com projetos locais
```

### 4.4 Memória operacional

```text
- tarefas recorrentes
- comandos frequentes
- documentos importantes
- modelos de proposta
- padrões de atendimento
- fornecedores usados
- produtos vendidos pela agência
- perfil dos clientes
```

---

## 5. Ferramentas do Jarvis

O verdadeiro poder do Jarvis está nas ferramentas que ele pode executar.

### 5.1 Ferramentas do sistema

```text
abrir_programa()
abrir_site()
executar_comando_terminal()
listar_processos()
verificar_status_docker()
abrir_projeto_vscode()
```

### 5.2 Ferramentas de arquivos

```text
pesquisar_arquivo()
ler_arquivo()
criar_arquivo()
mover_arquivo()
renomear_arquivo()
resumir_documento()
```

### 5.3 Ferramentas de navegador

```text
abrir_url()
pesquisar_google()
coletar_dados_site()
preencher_formulario()
executar_fluxo_playwright()
```

### 5.4 Ferramentas de produtividade

```text
criar_tarefa()
criar_lembrete()
criar_evento_calendario()
gerar_documento()
gerar_markdown()
gerar_pdf()
```

### 5.5 Ferramentas técnicas

```text
consultar_postgres()
gerar_sql()
explicar_erro_docker()
rodar_comando_git()
abrir_repositorio()
criar_branch()
criar_commit()
```

### 5.6 Ferramentas para a MV Travel

```text
criar_roteiro_viagem()
gerar_proposta_cliente()
montar_pacote_experiencia()
gerar_post_instagram()
gerar_legenda()
gerar_script_reels()
organizar_leads()
criar_checklist_viagem()
```

---

## 6. Segurança e permissões

O Jarvis deve classificar ações por risco.

### 6.1 Baixo risco

Pode executar diretamente:

```text
- abrir aplicativo
- abrir site
- ler arquivo
- pesquisar documento
- consultar agenda
```

### 6.2 Médio risco

Deve pedir confirmação:

```text
- enviar e-mail
- criar evento
- mover arquivo
- alterar documento
- executar comando git
```

### 6.3 Alto risco

Deve sempre pedir confirmação explícita:

```text
- apagar arquivo
- executar comando destrutivo
- alterar banco de dados
- enviar mensagem para cliente
- comprar passagem
- fazer pagamento
- publicar post
- alterar produção
```

Exemplo de confirmação:

```text
Wilson, essa ação pode alterar arquivos do projeto. Posso continuar?
```

---

## 7. Estrutura sugerida do projeto

```text
jarvis/
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── audio/
│   │   ├── hotword.py
│   │   ├── recorder.py
│   │   └── speaker.py
│   │
│   ├── agent/
│   │   ├── brain.py
│   │   ├── prompts.py
│   │   ├── memory.py
│   │   └── orchestrator.py
│   │
│   ├── tools/
│   │   ├── system_tools.py
│   │   ├── file_tools.py
│   │   ├── browser_tools.py
│   │   ├── email_tools.py
│   │   ├── calendar_tools.py
│   │   ├── travel_tools.py
│   │   ├── database_tools.py
│   │   └── git_tools.py
│   │
│   ├── security/
│   │   ├── permissions.py
│   │   └── confirmations.py
│   │
│   ├── storage/
│   │   ├── memory.db
│   │   └── logs.db
│   │
│   └── ui/
│       └── tray.py
│
├── docs/
│   ├── arquitetura.md
│   ├── memoria.md
│   ├── ferramentas.md
│   └── roadmap.md
│
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 8. Stack recomendada

### Linguagem principal

```text
Python
```

### Ambiente do usuário

```text
MacBook Pro M4 Pro
macOS
VS Code
Docker
PostgreSQL
```

### IA e voz

```text
OpenAI Realtime API
OpenAI Agents SDK
OpenAI TTS
Whisper / whisper.cpp
Ollama local como alternativa
```

### Automação

```text
subprocess
AppleScript
Playwright
pyautogui
```

### Banco e memória

```text
SQLite no MVP
PostgreSQL em versão avançada
Vector database em versão futura
```

### Controle de versão

```text
Git
GitHub
```

---

## 9. Roadmap de desenvolvimento

### Fase 1 — MVP de voz

Objetivo: fazer o Jarvis acordar, ouvir e responder.

Tarefas:

```text
- configurar projeto Python
- configurar ambiente virtual
- criar README.md
- configurar .env
- implementar hotword
- capturar áudio
- integrar com modelo de IA
- responder por voz
```

### Fase 2 — Ferramentas básicas

Objetivo: permitir ações simples no computador.

Tarefas:

```text
- abrir programas
- abrir sites
- listar arquivos
- criar arquivos markdown
- executar comandos seguros
- abrir projetos no VS Code
```

### Fase 3 — Memória

Objetivo: fazer o Jarvis lembrar contexto pessoal e profissional.

Tarefas:

```text
- criar banco SQLite
- salvar preferências
- salvar histórico de comandos
- consultar memória antes de responder
- criar categorias de memória
```

### Fase 4 — Segurança

Objetivo: impedir ações perigosas sem autorização.

Tarefas:

```text
- classificar ferramentas por risco
- criar camada de confirmação
- registrar logs
- bloquear comandos proibidos
- exigir confirmação para ações sensíveis
```

### Fase 5 — Integração com GitHub

Objetivo: conectar o Jarvis ao repositório GitHub.

Repositório:

```text
https://github.com/wilsonnettoo/jarvis.git
```

Tarefas:

```text
- clonar repositório
- criar estrutura inicial
- adicionar README.md
- criar .gitignore
- criar requirements.txt
- fazer primeiro commit
- enviar para GitHub
```

### Fase 6 — Jarvis técnico

Objetivo: ajudar no trabalho de desenvolvimento.

Tarefas:

```text
- explicar erros de Docker
- consultar PostgreSQL
- gerar comandos SQL
- abrir projeto no VS Code
- criar branches
- gerar commits
- analisar logs
```

### Fase 7 — Jarvis MV Travel

Objetivo: ajudar na operação da agência.

Tarefas:

```text
- criar roteiros personalizados
- gerar propostas comerciais
- criar posts para Instagram
- gerar scripts de Reels
- organizar leads
- gerar checklists de viagem
- criar modelos de atendimento
```

---

## 10. Comandos para adicionar este README ao GitHub

### 10.1 Clonar o repositório

```bash
git clone https://github.com/wilsonnettoo/jarvis.git
cd jarvis
```

### 10.2 Criar o README.md

Copie este arquivo para dentro da pasta do projeto com o nome:

```text
README.md
```

### 10.3 Adicionar arquivos ao Git

```bash
git add README.md
```

### 10.4 Criar o primeiro commit

```bash
git commit -m "docs: adiciona planejamento inicial do Jarvis"
```

### 10.5 Enviar para o GitHub

```bash
git push origin main
```

Se o branch principal for `master`, use:

```bash
git push origin master
```

---

## 11. Comandos completos em sequência

```bash
git clone https://github.com/wilsonnettoo/jarvis.git
cd jarvis

# copie o README.md para esta pasta antes de continuar

git status
git add README.md
git commit -m "docs: adiciona planejamento inicial do Jarvis"
git push origin main
```

---

## 12. Próximo passo recomendado

Após adicionar este README no GitHub, o próximo passo é criar a estrutura inicial do projeto:

```bash
mkdir -p app/audio app/agent app/tools app/security app/storage app/ui docs tests
touch app/main.py app/config.py
touch app/audio/hotword.py app/audio/recorder.py app/audio/speaker.py
touch app/agent/brain.py app/agent/prompts.py app/agent/memory.py app/agent/orchestrator.py
touch app/tools/system_tools.py app/tools/file_tools.py app/tools/browser_tools.py app/tools/travel_tools.py app/tools/database_tools.py app/tools/git_tools.py
touch app/security/permissions.py app/security/confirmations.py
touch docs/arquitetura.md docs/memoria.md docs/ferramentas.md docs/roadmap.md
touch requirements.txt .env.example .gitignore
```

Depois:

```bash
git add .
git commit -m "chore: cria estrutura inicial do projeto Jarvis"
git push origin main
```

---

## 13. Filosofia do projeto

O Jarvis deve ser construído com três princípios:

```text
1. Utilidade real antes de sofisticação
2. Segurança antes de autonomia
3. Memória personalizada antes de respostas genéricas
```

A primeira meta não é criar um assistente perfeito. A primeira meta é criar um assistente simples, confiável e capaz de executar poucas tarefas muito bem.

