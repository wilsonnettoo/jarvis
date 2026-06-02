# Jarvis Agentic Core — Sistema Meta-Agente com Fábrica de Agentes

## 1. Visão Geral

O objetivo deste projeto é criar um sistema de IA capaz de conversar com o usuário, entender o objetivo da conversa, transformar esse objetivo em tarefas práticas e acionar agentes especializados para executar o trabalho.

A ideia central não é criar apenas um chatbot, mas sim um **sistema operacional de agentes de IA**, onde a conversa inicial vira planejamento, execução, revisão e aprendizado contínuo.

O sistema deve ser capaz de:

- Entender conversas em linguagem natural.
- Identificar o que precisa ser feito.
- Verificar se já existe um agente adequado para a tarefa.
- Reutilizar agentes existentes para evitar duplicidade.
- Criar novos agentes somente quando necessário.
- Permitir que agentes peçam ajuda a outros agentes.
- Controlar a comunicação entre agentes por meio de um orquestrador central.
- Guardar memória de projetos, tarefas e decisões.
- Exigir aprovação humana antes de ações sensíveis.
- Evitar loops infinitos, criação descontrolada de agentes e desperdício de custo.

---

## 2. Nome Conceitual da Arquitetura

### Nome técnico

**Sistema Meta-Agente com Fábrica de Agentes**

### Nome para o projeto Jarvis

**Jarvis Agentic Core**

### Definição curta

O **Jarvis Agentic Core** é uma arquitetura multiagente onde um agente principal entende os objetivos do usuário, planeja as ações necessárias, reutiliza agentes existentes e cria novos agentes especializados quando necessário.

---

## 3. Conceito Principal

O sistema funciona a partir de um agente central chamado **Orquestrador Mestre**.

Esse agente não executa tudo sozinho. Ele atua como coordenador.

Ele faz perguntas como:

- O que o usuário realmente quer?
- Isso é uma tarefa simples ou um projeto?
- Quais etapas precisam ser executadas?
- Já existe algum agente especializado nessa tarefa?
- Preciso criar um agente novo?
- Quais ferramentas esse agente pode usar?
- Essa ação exige aprovação humana?
- Qual é o resultado esperado?
- O trabalho final está bom o suficiente para entregar?

---

## 4. Fluxo Geral do Sistema

```text
Usuário
  ↓
Agente Conversacional
  ↓
Orquestrador Mestre
  ↓
Análise de intenção
  ↓
Criação do plano de trabalho
  ↓
Consulta ao Agent Registry
  ↓
Reutilização ou criação de agentes
  ↓
Execução das tarefas
  ↓
Revisão
  ↓
Entrega ao usuário
```

---

## 5. Exemplo Prático

### Entrada do usuário

```text
Jarvis, quero criar uma campanha para vender pacotes de Orlando em julho.
```

### O sistema entende

```text
Objetivo: criar campanha comercial de turismo
Produto: pacotes de Orlando
Período: julho
Canal provável: Instagram, WhatsApp, Facebook e anúncios
Necessidades: pesquisa, oferta, copy, design, funil e revisão
```

### O Orquestrador divide em tarefas

```text
1. Pesquisar tendências de Orlando e Disney.
2. Analisar concorrentes.
3. Criar proposta de oferta.
4. Criar textos comerciais.
5. Criar calendário de posts.
6. Criar sequência de WhatsApp.
7. Revisar a campanha.
8. Entregar para aprovação.
```

### O sistema consulta agentes existentes

```text
Já existe agente de pesquisa de turismo? Sim.
Já existe agente de copywriting? Sim.
Já existe agente de Instagram? Sim.
Já existe agente de tráfego pago para turismo? Não.
```

### O sistema decide

```text
Reutilizar:
- Agente de Pesquisa de Turismo
- Agente de Copywriting
- Agente de Instagram
- Agente Revisor

Criar:
- Agente de Tráfego Pago para Turismo
```

---

## 6. Componentes da Arquitetura

## 6.1 Agente Conversacional

É a interface direta com o usuário.

Responsabilidades:

- Conversar em português natural.
- Entender comandos vagos ou diretos.
- Capturar objetivos.
- Transformar conversas em intenções.
- Encaminhar demandas para o Orquestrador Mestre.
- Entregar respostas finais ao usuário.

Exemplos de entrada:

```text
Quero vender mais Disney.
Monte uma campanha para Orlando.
Analise meus concorrentes.
Crie uma proposta para um cliente.
Organize meu CRM.
Pesquise os melhores destinos para julho.
```

---

## 6.2 Orquestrador Mestre

É o cérebro gerencial do sistema.

Responsabilidades:

- Interpretar o objetivo do usuário.
- Criar plano de execução.
- Dividir objetivos grandes em tarefas menores.
- Consultar o Agent Registry.
- Reutilizar agentes existentes.
- Autorizar ou negar criação de novos agentes.
- Coordenar comunicação entre agentes.
- Controlar limites de custo, tempo e profundidade.
- Acionar revisão final.
- Solicitar aprovação humana quando necessário.

Regra principal:

```text
Nenhum agente cria outro agente diretamente.
Todo pedido de criação passa pelo Orquestrador Mestre.
```

---

## 6.3 Agent Registry

É o cadastro central dos agentes existentes.

Serve para evitar agentes repetidos.

O registro deve guardar:

- Nome do agente.
- Função.
- Especialidade.
- Ferramentas permitidas.
- Memória relacionada.
- Tarefas anteriores.
- Projetos em que atuou.
- Qualidade das entregas.
- Status: ativo, pausado ou arquivado.
- Data de criação.
- Última utilização.

Exemplo de agente registrado:

```json
{
  "name": "agente_copy_orlando",
  "role": "Copywriter especializado em pacotes Orlando e Disney",
  "skills": ["copywriting", "turismo", "Disney", "Instagram", "WhatsApp"],
  "tools": ["web_search", "crm_read", "docs_writer"],
  "status": "active"
}
```

---

## 6.4 Agent Factory

É a fábrica de agentes.

Ela cria novos agentes somente quando o Orquestrador decide que não existe um agente adequado.

Cada agente novo precisa nascer com um contrato claro.

Contrato mínimo de criação:

```text
Nome
Missão
Especialidade
Ferramentas permitidas
Ações proibidas
Formato de saída
Critérios de qualidade
Quando pedir ajuda
Quando parar
```

Exemplo:

```json
{
  "name": "agente_trafego_pago_turismo",
  "mission": "Criar campanhas de tráfego pago para produtos turísticos",
  "specialty": "Meta Ads para pacotes de viagem",
  "allowed_tools": ["web_search", "audience_research", "campaign_planner"],
  "forbidden_actions": ["publicar anúncio sem aprovação", "alterar orçamento sem autorização"],
  "output_format": "plano de campanha com público, criativos, verba e copy",
  "status": "active"
}
```

---

## 6.5 Memória do Sistema

O sistema deve ter três níveis de memória.

### 6.5.1 Memória Curta

É a memória da conversa atual.

Exemplo:

```text
O usuário está planejando uma campanha de Orlando para julho.
```

Duração: sessão atual.

---

### 6.5.2 Memória de Projeto

É a memória de um projeto específico.

Exemplo:

```text
Projeto: Campanha Orlando Julho 2026
Produto: pacote Disney
Público-alvo: famílias brasileiras
Canais: Instagram, WhatsApp e anúncios
Status: em planejamento
```

Duração: enquanto o projeto existir.

---

### 6.5.3 Memória Permanente

É a memória de informações estáveis sobre o usuário e o negócio.

Exemplo:

```text
Wilson trabalha com a agência MV Travel.
A agência foca em viagens de experiência.
O usuário prefere português do Brasil.
O usuário usa MacBook Pro M4 Pro.
O usuário usa PostgreSQL, Docker e VS Code.
O usuário gosta de comandos práticos.
```

Duração: longo prazo.

---

## 6.6 Comunicação entre Agentes

A comunicação deve ser controlada.

Modelo recomendado:

```text
Agente A → Orquestrador → Agente B
Agente B → Orquestrador → Agente C
```

Evitar:

```text
Agente A ↔ Agente B ↔ Agente C ↔ Agente D
```

Motivo:

Quando todos os agentes conversam livremente entre si, o sistema pode ficar caro, confuso e difícil de auditar.

O Orquestrador deve ser o ponto central de controle.

---

## 7. Tipos de Agentes Iniciais

Para o MVP, começar com poucos agentes fixos.

## 7.1 Orquestrador Mestre

Função:

- Entender o objetivo.
- Planejar.
- Delegar.
- Controlar.
- Revisar fluxo geral.

---

## 7.2 Agente Pesquisador

Função:

- Pesquisar informações.
- Coletar dados.
- Levantar referências.
- Comparar fontes.
- Identificar oportunidades.

Exemplos de uso:

- Pesquisar destinos em alta.
- Analisar concorrentes.
- Levantar preços.
- Identificar tendências de turismo.

---

## 7.3 Agente Planejador

Função:

- Transformar pesquisa em plano.
- Criar etapas.
- Definir prioridades.
- Montar cronogramas.
- Estruturar execução.

Exemplos de uso:

- Criar plano de campanha.
- Montar roteiro de projeto.
- Organizar tarefas.
- Criar checklist.

---

## 7.4 Agente Executor

Função:

- Produzir entregáveis.
- Criar textos.
- Montar documentos.
- Gerar estruturas.
- Preparar arquivos.

Exemplos de uso:

- Criar posts.
- Gerar e-mails.
- Montar scripts.
- Criar propostas.
- Produzir documentação.

---

## 7.5 Agente Revisor

Função:

- Validar qualidade.
- Conferir coerência.
- Checar se a entrega atende ao objetivo.
- Identificar falhas.
- Sugerir melhorias.

---

## 8. Agentes Especializados Futuramente

Depois do MVP, criar agentes especializados por área.

### Marketing

```text
Agente de Copywriting
Agente de Instagram
Agente de Facebook
Agente de TikTok
Agente de Tráfego Pago
Agente de Funil de Vendas
Agente de Calendário Editorial
```

### Turismo

```text
Agente de Disney e Orlando
Agente de Roteiros Personalizados
Agente de Passagens Aéreas
Agente de Hotéis
Agente de Seguro Viagem
Agente de Vistos
Agente de Experiências Premium
```

### Operação da Agência

```text
Agente de CRM
Agente de Atendimento WhatsApp
Agente de Propostas Comerciais
Agente de Pós-venda
Agente de Documentação
Agente de Financeiro
```

### Desenvolvimento

```text
Agente Programador
Agente DevOps
Agente Banco de Dados
Agente QA
Agente Documentador Técnico
```

---

## 9. Banco de Dados Recomendado

Como o projeto pode usar PostgreSQL, a estrutura inicial pode ser:

```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    mission TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE agent_skills (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    skill TEXT NOT NULL
);

CREATE TABLE agent_tools (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    tool_name TEXT NOT NULL,
    permission_level TEXT NOT NULL
);

CREATE TABLE agent_tasks (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    project_id UUID,
    task_description TEXT NOT NULL,
    status TEXT NOT NULL,
    result TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    finished_at TIMESTAMP
);

CREATE TABLE agent_memory (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE agent_messages (
    id UUID PRIMARY KEY,
    project_id UUID,
    from_agent_id UUID,
    to_agent_id UUID,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE agent_performance (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    task_id UUID REFERENCES agent_tasks(id),
    quality_score NUMERIC,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

Observação:

Para usar busca vetorial dentro do PostgreSQL, pode ser usado o `pgvector`.

---

## 10. Regras de Segurança

O sistema precisa de limites claros.

## 10.1 Limite de Criação de Agentes

```text
Um agente não pode criar outro agente diretamente.
Ele só pode solicitar ao Orquestrador.
```

---

## 10.2 Limite de Profundidade

Exemplo:

```text
Profundidade máxima: 3 níveis
Usuário → Orquestrador → Agente → Subtarefa
```

Evitar:

```text
Usuário → Agente → Agente → Agente → Agente → Agente
```

---

## 10.3 Limite de Custo

Cada projeto deve ter orçamento máximo.

Exemplo:

```text
Custo máximo por tarefa: R$ 5,00
Custo máximo por projeto: R$ 50,00
```

---

## 10.4 Limite de Tempo

Exemplo:

```text
Tempo máximo por tarefa: 5 minutos
Tempo máximo por projeto: 30 minutos
```

---

## 10.5 Aprovação Humana

Ações que exigem aprovação:

```text
Enviar e-mail
Publicar post
Rodar anúncio
Comprar algo
Alterar banco de dados
Excluir arquivos
Enviar mensagem para cliente
Acessar dados sensíveis
Alterar orçamento
```

---

## 10.6 Logs Obrigatórios

Tudo deve ser registrado:

```text
Quem pediu
O que foi pedido
Qual agente executou
Quais ferramentas usou
Qual decisão tomou
Qual foi o resultado
Quanto custou
Quanto tempo levou
```

---

## 11. Stack Técnica Recomendada

## 11.1 Backend

```text
Python
FastAPI
LangGraph
OpenAI Agents SDK
Pydantic
SQLAlchemy
```

---

## 11.2 Banco de Dados

```text
PostgreSQL
pgvector
Redis
```

---

## 11.3 Interface

```text
React
Next.js
Tailwind CSS
```

---

## 11.4 Infraestrutura Local

```text
Docker
Docker Compose
VS Code
MacBook Pro M4 Pro
```

---

## 11.5 Observabilidade

```text
Logs próprios
OpenTelemetry
LangSmith
Painel administrativo
```

---

## 12. Estrutura de Pastas

```text
jarvis-agentic-core/
  apps/
    api/
      main.py
      routes/
      services/
      schemas/
    web/
      app/
      components/
      pages/
  core/
    orchestrator/
      master_orchestrator.py
      task_planner.py
      delegation_engine.py
    agent_factory/
      factory.py
      templates.py
      validation.py
    agent_registry/
      registry.py
      similarity_search.py
    memory/
      short_term.py
      project_memory.py
      long_term_memory.py
      vector_store.py
    tools/
      web_search.py
      crm.py
      email.py
      calendar.py
      files.py
    guardrails/
      permissions.py
      cost_limits.py
      approval_rules.py
    evaluators/
      quality_checker.py
      duplication_checker.py
  agents/
    marketing/
    travel/
    coding/
    research/
    finance/
  database/
    migrations/
    seeds/
  docs/
    architecture.md
    roadmap.md
    prompts.md
  docker-compose.yml
  README.md
```

---

## 13. Modelo de Decisão do Orquestrador

O Orquestrador deve seguir esta lógica:

```text
1. Receber a solicitação do usuário.
2. Identificar o objetivo principal.
3. Classificar o tipo de tarefa.
4. Verificar se é tarefa simples ou projeto.
5. Quebrar em subtarefas.
6. Consultar agentes existentes.
7. Medir similaridade entre tarefa e agentes cadastrados.
8. Reutilizar agente se houver compatibilidade.
9. Criar novo agente se não houver compatibilidade.
10. Definir ferramentas permitidas.
11. Executar tarefas.
12. Revisar resultados.
13. Consolidar entrega.
14. Pedir aprovação humana se necessário.
15. Salvar aprendizados na memória.
```

---

## 14. Como Evitar Agentes Repetidos

Antes de criar um novo agente, o sistema deve comparar:

```text
Nome
Missão
Habilidades
Tipo de tarefa
Histórico de uso
Ferramentas
Área de atuação
```

Critério sugerido:

```text
Se similaridade for maior que 80%, reutilizar agente existente.
Se similaridade estiver entre 60% e 80%, pedir decisão do Orquestrador.
Se similaridade for menor que 60%, permitir criação de novo agente.
```

Exemplo:

```text
Pedido: criar campanha para Disney

Agente existente:
Nome: agente_copy_orlando
Missão: criar textos comerciais para pacotes Orlando e Disney

Decisão:
Reutilizar agente existente.
```

---

## 15. Roadmap de Desenvolvimento

## Fase 1 — MVP Simples

Objetivo:

Criar um sistema inicial com agentes fixos.

Componentes:

```text
Agente Conversacional
Orquestrador Mestre
Agente Pesquisador
Agente Planejador
Agente Executor
Agente Revisor
PostgreSQL
API FastAPI
Interface simples
```

Resultado esperado:

O usuário conversa com o sistema, o sistema cria um plano e distribui tarefas entre agentes fixos.

---

## Fase 2 — Agent Registry

Objetivo:

Registrar agentes e reutilizá-los.

Componentes:

```text
Tabela agents
Tabela agent_skills
Tabela agent_tools
Tabela agent_tasks
Busca por similaridade
Histórico de uso
```

Resultado esperado:

Antes de criar ou usar agentes, o sistema consulta o registro.

---

## Fase 3 — Agent Factory

Objetivo:

Permitir criação dinâmica de agentes.

Componentes:

```text
Templates de agentes
Validador de duplicidade
Contrato de criação
Permissões por agente
Status ativo/arquivado
```

Resultado esperado:

O sistema cria novos agentes somente quando necessário.

---

## Fase 4 — Memória Vetorial

Objetivo:

Adicionar memória inteligente.

Componentes:

```text
pgvector
Embeddings
Memória de projeto
Memória permanente
Busca semântica
```

Resultado esperado:

O sistema lembra decisões, projetos, preferências e entregas anteriores.

---

## Fase 5 — Ferramentas Reais

Objetivo:

Permitir que agentes executem tarefas práticas.

Ferramentas possíveis:

```text
Web search
Gmail
Google Calendar
Google Drive
Canva
CRM da MV Travel
PostgreSQL
GitHub
WhatsApp API
ManyChat
```

Resultado esperado:

Os agentes passam a executar tarefas de trabalho real, com aprovação humana.

---

## Fase 6 — Painel Administrativo

Objetivo:

Visualizar e controlar agentes.

Tela ideal:

```text
Lista de agentes
Status dos agentes
Tarefas em andamento
Custos
Logs
Memórias
Projetos
Aprovações pendentes
```

Resultado esperado:

O usuário consegue controlar todo o sistema visualmente.

---

## 16. Primeiro MVP Recomendado

O primeiro MVP deve ser simples.

Não começar com criação infinita de agentes.

Começar com:

```text
1. Uma conversa com o usuário.
2. Um Orquestrador Mestre.
3. Quatro agentes fixos:
   - Pesquisador
   - Planejador
   - Executor
   - Revisor
4. Um banco PostgreSQL.
5. Registro de tarefas.
6. Memória simples.
7. Entrega final em Markdown.
```

Depois disso, evoluir para Agent Registry e Agent Factory.

---

## 17. Exemplo de Prompt do Orquestrador Mestre

```text
Você é o Orquestrador Mestre do Jarvis Agentic Core.

Sua função é entender o objetivo do usuário, dividir o trabalho em tarefas, escolher os agentes corretos e coordenar a execução.

Você não deve executar tudo sozinho.

Antes de criar um novo agente, verifique se já existe um agente adequado no Agent Registry.

Nenhum agente pode criar outro agente diretamente.

Sempre que uma ação envolver envio de mensagem, publicação, compra, alteração de banco, exclusão de arquivos ou contato com clientes, solicite aprovação humana.

Sua resposta deve conter:
1. Objetivo identificado.
2. Plano de execução.
3. Agentes necessários.
4. Agentes existentes a reutilizar.
5. Agentes novos a criar, se necessário.
6. Riscos.
7. Próximo passo recomendado.
```

---

## 18. Exemplo de Prompt para Agente Especializado

```text
Você é um agente especializado do Jarvis Agentic Core.

Missão:
Executar uma tarefa específica delegada pelo Orquestrador Mestre.

Regras:
- Não crie outros agentes.
- Se precisar de ajuda, solicite ao Orquestrador.
- Use apenas as ferramentas permitidas.
- Não execute ações sensíveis sem autorização.
- Entregue resultados objetivos.
- Informe limitações, dúvidas e riscos.
- Salve aprendizados relevantes na memória do projeto.

Formato de resposta:
1. Tarefa recebida.
2. Ações executadas.
3. Resultado.
4. Pendências.
5. Sugestões.
```

---

## 19. Princípio Central

O sistema não deve ser:

```text
Um monte de agentes soltos conversando sem controle.
```

O sistema deve ser:

```text
Um orquestrador central coordenando agentes especialistas reutilizáveis.
```

Agentes soltos criam caos.

Agentes coordenados criam produtividade.

---

## 20. Resumo Final

O projeto ideal para o Wilson é um **Jarvis Agentic Core**, um sistema de IA multiagente com:

- Conversa natural.
- Orquestrador central.
- Registro de agentes.
- Fábrica de agentes.
- Memória curta, de projeto e permanente.
- Reutilização de agentes.
- Comunicação controlada.
- Aprovação humana para ações sensíveis.
- Banco PostgreSQL.
- Interface web.
- Integração futura com Gmail, Calendar, Canva, WhatsApp, CRM e GitHub.

A primeira versão deve ser simples, controlada e funcional.

O objetivo inicial é provar que uma conversa pode virar:

```text
objetivo → plano → tarefas → agentes → execução → revisão → entrega
```

Depois disso, o sistema pode evoluir para autonomia maior, sempre com segurança, limites e controle humano.
