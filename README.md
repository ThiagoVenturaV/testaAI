# 🏙️ Diagnóstico Territorial & Dashboard: Comunidade do Pilar (Recife - PE)
## CESAR Summer Job 2026 · Desafio 09 (Cidade PRIME)
### SECTI Recife & Prefeitura da Cidade do Recife

![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![GeoPandas](https://img.shields.io/badge/GeoPandas-0.14+-139C55?style=for-the-badge&logo=pandas&logoColor=white)

---

## 📌 Visão Geral do Projeto

Este repositório contém o **Diagnóstico Socioespacial Baseado em Evidências** e o **Dashboard de Ciência de Dados** desenvolvido para a **Comunidade e Conjunto Habitacional do Pilar**, localizada no Bairro do Recife (RPA 1). 

O projeto foi formulado no contexto do **Desafio 09 ("Como testar novas formas de inclusão social, digital e urbana na Ilha do Recife?")** do **CESAR Summer Job 2026**, combinando os pilares **Inclusive + Experimental + Monitorable** do framework *Cidade PRIME*.

A plataforma cruza dados históricos, arqueológicos, cadastrais (CadÚnico 2023) e geoespaciais (GIS Recife) para estruturar a base empírica necessária à concepção de novos pilotos de inclusão urbana.

---

## 📊 Principais Indicadores Mapeados

```
┌────────────────────────────────────────────────────────────────────────┐
│             RADIOGRAFIA EMPÍRICA DA COMUNIDADE DO PILAR               │
├─────────────────────────────────────┬──────────────────────────────────┤
│ Atendimentos no CadÚnico USF Pilar  │ 145 Famílias / Indivíduos        │
│ População Étnico-Racial Negra       │ 86,9% (68,3% Pardos / 18,6% Pretos│
│ Renda Per Capita Mensal Média       │ R$ 360,30 (Extrema vulnerabilidade│
│ Renda Familiar Total Média          │ R$ 734,19                        │
│ Dependência do Bolsa Família        │ 69,0% (100 famílias)             │
│ Gasto Médio com Alimentação         │ R$ 316,93 (43,1% do orçamento)   │
│ Área da ZEIS Pilar (Tipo I)         │ 2,9637 ha (Perímetro: 749,58m)   │
│ Pontos de Wi-Fi Conecta Recife      │ 0 na poligonal da ZEIS Pilar     │
│ Balanço Habitacional (URB / MCMV)   │ ~320 entregues + 112 (Quadra 55) │
│ Sítio Arqueológico (UFPE / IPHAN)   │ +150k achados / 100-130 ossadas  │
└─────────────────────────────────────┴──────────────────────────────────┘
```

---

## 🎨 Funcionalidades do Dashboard (`pilar_dashboard.py`)

O dashboard é construído em **Streamlit + Plotly + GeoPandas** utilizando o design system **Dark Glassmorphism Premium**:

1. **📊 Perfil Socioeconômico**: Donut chart étnico-racial (86,9% população negra), gráfico de comprometimento do orçamento familiar com alimentação (43,1%) e cards de análise socioeconômica.
2. **🏗️ Habitação, Território & Arqueologia**: Bar chart da evolução das habitações (~320 entregues até 2025 + 112 da Quadra 55 em 2026), painel bioarqueológico do Sítio Arqueológico do Pilar e waterfall de pavimentação.
3. **🗺️ Mapeamento Geoespacial**: Mapa dark interativo (Carto DarkMatter) com os pontos estratégicos do Pilar, Habitacionais (Papa Francisco e Quadra 55), Igreja (1680), Upinha, Creche Escola, Porto Digital, Moinho Recife e Forte do Brum.
4. **🚨 Lacunas para Formulação de Pilotos**: Mapeamento de 4 eixos reais de vulnerabilidade (*Exclusão Digital, Barreiras Urbanas, Desconexão com Porto Digital e Apagamento Histórico*) com diretrizes orientadoras.
5. **📋 Explorador de Dados Brutos**: Tabela interativa para navegação e filtro dos microdados do CadÚnico 2023, Logradouros, ZEIS e Praças.

---

## 📁 Estrutura do Repositório

```
testaAI/
├── pilar_dashboard.py        # Aplicação Principal Streamlit (Dashboard Dark Glassmorphism)
├── extract_pilar_rich.py     # Script de extração e tratamento dos dados abertos GIS
├── pilar_rich_data.json      # Dados consolidados em formato JSON
├── requirements.txt          # Dependências do projeto Python
└── README.md                 # Documentação oficial do repositório
```

---

## 🛠️ Como Executar o Projeto Localmente

> O fluxo oficial de dados está documentado em [`TRATAMENTO_DE_DADOS.md`](TRATAMENTO_DE_DADOS.md). O dashboard territorial não lê mais as bases brutas diretamente: primeiro execute o pipeline.

### Pró-requisitos
- Python 3.10 ou superior
- Git

### 1. Clonar o Repositório
```bash
git clone https://github.com/ThiagoVenturaV/testaAI.git
cd testaAI
```

### 2. Criar Ambiente Virtual (Opcional, mas recomendado)
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/macOS:
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Executar o Dashboard
```bash
python pipeline_dados.py
streamlit run pilar_dashboard.py
```

Acesse a interface no navegador em: `http://localhost:8501`

---

## 📚 Fontes de Dados e Referências

* **PREFEITURA DO RECIFE**: Hub de Dados Abertos (CadÚnico 2023, Zoneamento ZEIS, ZEPH 09, Logradouros, Wi-Fi Conecta Recife).
* **IPHAN / UFPE**: Relatórios de Escavação Arqueológica do Sítio Pilar e Dossiê de Tombamento da Igreja de N. Sra. do Pilar (1680).
* **URB RECIFE**: Programa de Requalificação Urbanística e Inclusão Social da Comunidade do Pilar (PRUISCP).
* **CESAR / SECTI RECIFE**: Edital Summer Job 2026 — Desafio 09 (Ilha do Recife / Cidade PRIME).

---

<p align="center">
  Desenvolvido para o <b>CESAR Summer Job 2026</b> · Prefeitura da Cidade do Recife · SECTI
</p>
