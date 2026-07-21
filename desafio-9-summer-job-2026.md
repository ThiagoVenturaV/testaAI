# Desafio 9 — Summer Job 2026 (Cidade PRIME / Ilha do Recife)

## Contexto do desafio

**Pergunta oficial:** "Como testar novas formas de inclusão social, digital e urbana na Ilha do Recife?"

**Pilares combinados:** Inclusive + Experimental (a solução também incorpora Monitorable)

**Programa:** CESAR Summer Job 2026 + Prefeitura do Recife (SECTI), 20 a 31 de julho de 2026, na Ilha do Recife. 40 vagas, metodologia learn by doing. Entregáveis esperados: diagnóstico, hipóteses de intervenção, proposta de solução, demonstração de viabilidade.

**Framework Cidade PRIME (5 pilares):** Playable, Resilient, Inclusive, Monitorable, Experimental — cada desafio combina no mínimo 2 pilares; quanto mais pilares, maior o potencial de transformação.

---

## Evolução da ideia

1. **Ponto de partida:** soluções pontuais de inclusão (app de barreiras, sandbox sensorial, canal de participação cidadã).
2. **Pivô 1:** em vez de uma solução isolada, construir uma **plataforma de observabilidade** para que outros atores (ONGs, comércios, poder público, outros times) testem e meçam pilotos de inclusão — trazendo o pilar Monitorable pra dentro do desafio.
3. **Pivô 2:** trocar WhatsApp por **formulário web + QR code** como canal de captação — menor fricção de setup (sem aprovação de WhatsApp Business API/Twirlio).
4. **Pivô 3:** a plataforma não deveria ser um canal de reclamação — deveria ser o **motor de teste de uma inovação real**, com hipótese e KPI de sucesso definidos antes do teste.
5. **Pivô 4 (modelo final):** generalizar a plataforma como **infraestrutura de experimentação** — não amarrada a uma inovação específica, mas capaz de capturar dados de qualquer piloto de inclusão (dos participantes ou de terceiros).
6. **Refinamento final:** garantir que a plataforma seja **plugável em soluções já existentes**, sem precisar reescrevê-las — via link/QR code, webhook/API REST, ou uso nativo em pilotos novos.

---

## Conceito final da solução

**Uma plataforma genérica de experimentação e observabilidade para pilotos de inclusão na Ilha do Recife**, onde qualquer inovação (existente ou nova) pode se conectar para ser testada e medida com rigor.

### Modelo de dados (genérico)

```
Piloto
├── id, nome, descrição
├── hipótese (o que se espera provar)
├── responsável
├── KPI(s) definidos (métrica de sucesso, meta)
├── status (planejado → em teste → concluído → escalado/descartado)
└── Eventos (N por piloto)
     ├── timestamp
     ├── tipo de evento (conclusão, abandono, feedback, uso, etc.)
     ├── dados brutos (texto livre, número, geolocalização, foto)
     └── categoria (via IA, se aplicável)
```

### Pilares funcionais

- **Rastreabilidade** — ciclo de vida documentado de cada piloto (hipótese → intervenção → dados → resultado → decisão)
- **Observabilidade** — dashboard central mostrando pilotos ativos, alcance e resultados em tempo real
- **KPIs padronizados e comparáveis entre pilotos** — alcance segmentado, representatividade, redução de barreira, taxa de engajamento/conclusão, custo por pessoa impactada, índice de replicabilidade
- **IA aplicada** — classificação/clustering de feedback aberto, análise de sentimento, detecção de padrões de abandono, geração automática de resumo executivo por piloto

### Arquitetura técnica

```
[Configuração]         [Captação]              [Processamento]         [Observabilidade]
Cadastro de Piloto  →  Formulário dinâmico  →  Classificação IA   →   Dashboard multi-piloto
(hipótese + KPI)       (QR code por piloto)     por piloto              Comparação entre pilotos
                                                                          Resumo executivo (IA)
```

- **Backend:** Node.js, endpoints genéricos `/pilotos` (CRUD) e `/pilotos/:id/eventos` (captura)
- **Banco:** Postgres — tabelas Piloto e Evento
- **IA:** Claude API para classificação de texto livre e geração de resumos
- **Frontend:** formulário dinâmico mobile-first + dashboard React (mapa de calor, KPIs, timeline, comparação entre pilotos)

### Níveis de integração (plugável, sem refazer soluções existentes)

1. **Mínimo (zero código):** QR code/link de captura ao fim da experiência da solução existente
2. **Médio (poucas linhas):** webhook/API REST — `POST /pilotos/{id}/eventos` com payload livre em JSON
3. **Nativo:** pilotos novos construídos já usando o SDK/API da plataforma diretamente

### Narrativa para o pitch

Não é "construímos uma solução de inclusão" — é **"construímos o protocolo de instrumentação da Cidade PRIME"**: qualquer inovação, existente ou futura, se conecta em minutos e passa a ser testável e mensurável, provando que a solução escala além da Ilha do Recife e além do Summer Job.

---

## Próximos passos em aberto

- Desenhar o contrato da API (endpoints + payload padrão) para o edital/pitch
- Cadastrar 1–2 pilotos reais próprios (ex.: rota acessível gamificada, trilha sensorial) para demonstrar a plataforma ponta a ponta
- Estruturar o schema do banco de dados (Piloto/Evento)
- Prototipar o dashboard multi-piloto
