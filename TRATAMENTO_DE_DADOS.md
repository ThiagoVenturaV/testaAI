# Tratamento de dados — Comunidade do Pilar

## 1. Visão geral

O tratamento das bases é executado por `pipeline_dados.py`. O pipeline lê os arquivos originais de `Fontes_Summerjob`, valida sua estrutura, padroniza tipos e textos, cria recortes territoriais e calcula os indicadores consumidos por `pilar_dashboard.py`.

O fluxo utiliza quatro níveis:

```text
Fontes_Summerjob/                  Bases originais
        |
        v
pipeline_dados.py                  Validação e processamento
        |
        +-- dados/02_tratados/     Tabelas padronizadas
        +-- dados/03_recortes/     Recortes do Pilar e do entorno
        `-- dados/04_indicadores/  Indicadores, catálogo e qualidade
                                           |
                                           v
                                pilar_dashboard.py
```

`Fontes_Summerjob` corresponde à camada de dados brutos. Os arquivos dessa pasta não são modificados pelo pipeline.

## 2. Motivação do tratamento

O tratamento de dados tem como motivação central produzir **insights confiáveis para testar novas formas de inclusão digital, social e urbana** na Comunidade do Pilar e em seu entorno.

As bases são organizadas para apoiar três eixos:

- **Inclusão digital:** identificar cobertura e ausência de infraestrutura digital, especialmente pontos públicos de Wi-Fi, e localizar áreas que podem receber novas ações;
- **Inclusão social:** compreender o perfil das pessoas e famílias atendidas pela USF Pilar por meio de renda, raça/cor, faixa etária, escolaridade, deficiência, Bolsa Família e outras características sociais;
- **Inclusão urbana:** analisar a ZEIS Pilar, equipamentos públicos, praças, intervenções urbanas e condições de pavimentação e acessibilidade no território.

Os indicadores e recortes permitem formular hipóteses, escolher públicos e locais prioritários, definir métricas de sucesso e acompanhar futuros projetos-piloto. O tratamento mantém as fontes, fórmulas e datas de geração identificadas para que os insights utilizados nesses testes sejam reproduzíveis.

### Motivação de cada etapa

| Etapa | Motivação |
|---|---|
| Preservação das bases originais | Manter uma referência íntegra para auditoria e reprodução das análises |
| Padronização de texto e encoding | Garantir que bairros, categorias e equipamentos sejam encontrados e agrupados corretamente |
| Conversão de tipos | Permitir cálculos consistentes de renda, área, extensão, metragem e ano |
| Validação de schema | Confirmar que os campos necessários para produzir os insights estão disponíveis |
| Relatório de qualidade | Evidenciar nulos, duplicidades e outras condições que afetam a interpretação dos resultados |
| Recorte do CadÚnico | Caracterizar o público vinculado à USF Nossa Senhora do Pilar |
| Recorte geoespacial | Identificar equipamentos dentro da ZEIS e em seu entorno imediato pela localização real |
| Indicadores rastreáveis | Relacionar cada resultado à sua fonte, território e fórmula |
| Filtros do dashboard | Permitir a exploração de diferentes públicos e apoiar a formulação de hipóteses de inclusão |
| Exportação dos recortes | Disponibilizar os grupos analisados para aprofundamentos e planejamento dos pilotos |

## 3. Execução

Na raiz do projeto:

```powershell
pip install -r requirements.txt
python pipeline_dados.py
streamlit run pilar_dashboard.py
```

Após qualquer atualização em `Fontes_Summerjob`, o pipeline deve ser executado novamente.

## 4. Bases utilizadas

| Identificador | Arquivo |
|---|---|
| CadÚnico | `cadastro-unico-2023.csv` |
| Bairros e RPAs | `bairros-e-rpas-do-recife.csv` |
| Parques e praças | `parques-e-pracas.csv` |
| Malha cicloviária | `detalhes-da-implantacao-da-malha-cicloviaria-do-recife.csv` |
| Urbanismo tático | `urbanismo-tatico-.csv` |
| Logradouros | `trechos-de-logradouros-por-bairro.csv` |
| Wi-Fi público | `localidades-do-conecta-recife-wifi.csv` |
| ZEIS | `zoneamento-plano-diretor-zeis.geojson` |

As demais bases permanecem disponíveis em `Fontes_Summerjob`, mas não participam do pipeline territorial atual.

## 5. Leitura e codificação

Os CSVs são lidos com detecção de separador e teste sequencial destas codificações:

1. `utf-8-sig`;
2. `utf-8`;
3. `latin1`.

O encoding aceito é registrado no catálogo. Os CSVs processados são gravados em `UTF-8-SIG`.

Os arquivos GeoJSON são lidos com GeoPandas. Quando a base ZEIS não informa um CRS, o pipeline atribui `EPSG:4326`.

## 6. Normalização de textos

A função `normalize_text` é usada para criar campos auxiliares de comparação. Ela:

- converte o valor para texto;
- aplica normalização Unicode NFKD;
- remove acentos na coluna auxiliar;
- converte para letras maiúsculas;
- remove espaços repetidos.

As colunas originais são preservadas. Entre as colunas auxiliares geradas está `bairro_normalizado`.

## 7. Conversão de valores

A função de conversão numérica:

1. transforma o campo em texto;
2. substitui vírgula decimal por ponto;
3. usa `pd.to_numeric(errors="coerce")`;
4. transforma valores inválidos em nulos.

Campos derivados:

| Base | Campos gerados |
|---|---|
| Praças | `area_m2`, `bairro_normalizado` |
| Ciclovias | `extensao_km`, `ano_inauguracao` |
| Urbanismo tático | `metragem_m` |
| Logradouros | `bairro_normalizado` |
| Wi-Fi | `bairro_normalizado` |
| Bairros e RPAs | `bairro_normalizado` |
| CadÚnico | ano, raça/cor, sexo, faixa etária, escolaridade, benefício, deficiência, situação de rua e rendas numéricas |

## 8. Validação das bases

O pipeline verifica a existência de colunas obrigatórias antes do processamento.

### CadÚnico

- `cod_familiar`
- `d.nom_estab_assist_saude_fam`
- `p.cod_raca_cor_pessoa`
- `dat_atualizacao`

### Bairros e RPAs

- `Bairro`
- `rpa`

### Praças

- `nome_bairro`
- `latitude`
- `longitude`
- `area`

### Ciclovias

- `rota`
- `tipologia`
- `bairros`
- `extensao`
- `inauguracao`

### Urbanismo tático

- `bairro`
- `latitude`
- `longitude`
- `ano`
- `tipo`

### Logradouros

- `nomeBairro`
- `desc_indica_pavimentacao`

### Wi-Fi

- `NOME`
- `BAIRRO`
- `LATITUDE`
- `LONGITUDE`

A ausência de uma coluna obrigatória interrompe a execução e informa a base e os campos ausentes.

## 9. Relatório de qualidade

Para cada CSV utilizado são calculados:

- total de registros;
- total de colunas;
- linhas integralmente duplicadas;
- total de células nulas;
- percentual de células nulas;
- encoding detectado;
- status de qualidade.

O relatório é salvo em:

```text
dados/04_indicadores/relatorio_qualidade.csv
```

O status é `aprovado_com_alertas` quando existem linhas duplicadas ou valores nulos. Caso contrário, é `aprovado`.

## 10. Recorte do CadÚnico

O recorte utiliza a coluna `d.nom_estab_assist_saude_fam`. São selecionadas as linhas em que o campo contém a palavra completa `PILAR`, sem diferenciação entre maiúsculas e minúsculas.

Na base atual, o estabelecimento encontrado é:

```text
US 278 USF NOSSA SRA DO PILAR BAIRRO DO RECIFE
```

O recorte contém 145 pessoas pertencentes a 73 famílias. Se nenhum registro do Pilar for localizado, a execução é interrompida.

O resultado é salvo em:

```text
dados/03_recortes/cadunico_pilar.csv
```

### Variáveis categóricas

Os códigos são convertidos nos seguintes rótulos:

- raça/cor: Branca, Preta, Amarela, Parda e Indígena;
- sexo: Masculino e Feminino;
- faixa etária: intervalos de 0 a 4 anos até 65 anos ou mais;
- escolaridade: sem instrução até médio completo ou superior;
- Bolsa Família: Sim ou Não;
- pessoa com deficiência: Sim ou Não;
- situação de rua: Sim ou Não.

O campo `ano_atualizacao` é extraído de `dat_atualizacao`.

Os campos `vlr_renda_media`, `vlr_renda_total` e `d.val_desp_alimentacao_fam` são convertidos para valores numéricos.

### Unidade de cálculo

Indicadores de pessoas usam todas as linhas do recorte. Indicadores familiares utilizam uma linha por `cod_familiar`.

## 11. Recorte geoespacial

A ZEIS Pilar é selecionada no GeoJSON de zoneamento pelo campo `NMNOME`. O nome deve conter a palavra completa `Pilar`.

O processo espacial utiliza estas etapas:

1. validação e reparo da geometria da ZEIS;
2. conversão do polígono e dos pontos para `EPSG:31985`;
3. criação de uma faixa de 500 metros ao redor da ZEIS;
4. classificação de cada ponto;
5. retorno das geometrias para `EPSG:4326` na exportação.

As classes territoriais são:

- `ZEIS Pilar`;
- `Entorno até 500 m`;
- `Fora do recorte`.

O recorte espacial é aplicado a:

- parques e praças;
- pontos de Wi-Fi;
- intervenções de urbanismo tático.

Antes da criação dos pontos, as coordenadas são convertidas para números e limitadas aproximadamente à área do Recife:

```text
longitude: -35,3 a -34,5
latitude:  -8,3 a -7,7
```

Somente as classes `ZEIS Pilar` e `Entorno até 500 m` são exportadas para `dados/03_recortes`.

## 12. Logradouros e pavimentação

Os logradouros são selecionados quando `bairro_normalizado` é igual a `RECIFE`.

O resultado é salvo em:

```text
dados/03_recortes/logradouros_bairro_recife.csv
```

O total de vias com déficit corresponde à soma das categorias:

- Via Não Pavimentada;
- Via Parcialmente Pavimentada.

## 13. Indicadores territoriais

Os indicadores são salvos em:

```text
dados/04_indicadores/indicadores_territoriais.csv
```

Cada linha possui:

- indicador;
- valor;
- unidade;
- território;
- fórmula;
- fonte;
- data e hora de geração em UTC.

### Fórmulas

| Indicador | Fórmula |
|---|---|
| Pessoas no CadÚnico | quantidade de linhas do recorte |
| Famílias no CadÚnico | quantidade de `cod_familiar` distintos |
| População negra | pessoas classificadas como Pretas ou Pardas ÷ pessoas do recorte |
| Famílias no Bolsa Família | famílias com `bolsa_familia = Sim` ÷ famílias do recorte |
| Renda per capita média | média de `vlr_renda_media` |
| Renda familiar média | média de `vlr_renda_total`, usando uma linha por família |
| Área da ZEIS Pilar | soma de `AREA_HA` da geometria selecionada |
| Wi-Fi na ZEIS | pontos classificados como `ZEIS Pilar` |
| Wi-Fi no entorno | pontos classificados como `Entorno até 500 m` |
| Vias com déficit | vias não pavimentadas + parcialmente pavimentadas |

## 14. Dashboard territorial

O arquivo `pilar_dashboard.py` lê somente as saídas existentes em `dados/03_recortes` e `dados/04_indicadores`.

### Filtros do CadÚnico

- raça/cor;
- ano de atualização cadastral;
- sexo;
- faixa etária;
- escolaridade;
- Bolsa Família;
- pessoa com deficiência;
- situação de rua;
- intervalo de renda per capita.

### Indicadores filtráveis

- pessoas;
- famílias;
- percentual de pessoas Pretas ou Pardas;
- percentual de famílias no Bolsa Família;
- renda per capita média;
- renda familiar média.

As rendas são exibidas no formato monetário brasileiro:

```text
R$ 1.020,30
```

### Visualizações

- distribuição por raça/cor;
- ano da última atualização cadastral;
- distribuição por faixa etária;
- distribuição por escolaridade;
- mapa de Wi-Fi, praças e urbanismo tático;
- situação de pavimentação;
- tabela de microdados filtrados;
- download do recorte filtrado;
- tabela de indicadores e fórmulas;
- relatório de qualidade.

## 15. Dashboard PRIME

O arquivo `prime_dashboard.py` é mantido como protótipo de monitoramento de futuros projetos-piloto. Ele não é executado pelo pipeline e suas simulações não participam dos indicadores territoriais.

## 16. Arquivos gerados

```text
dados/
├── 02_tratados/
│   ├── bairros_rpa.csv
│   ├── ciclovias.csv
│   ├── logradouros.csv
│   ├── pracas.csv
│   ├── urbanismo.csv
│   └── wifi.csv
├── 03_recortes/
│   ├── cadunico_pilar.csv
│   ├── logradouros_bairro_recife.csv
│   ├── pracas_pilar_entorno.csv
│   ├── pracas_pilar_entorno.geojson
│   ├── urbanismo_pilar_entorno.csv
│   ├── urbanismo_pilar_entorno.geojson
│   ├── wifi_pilar_entorno.csv
│   ├── wifi_pilar_entorno.geojson
│   └── zeis_pilar.geojson
└── 04_indicadores/
    ├── catalogo_bases.csv
    ├── indicadores_territoriais.csv
    ├── relatorio_qualidade.csv
    └── resumo_execucao.json
```

## 17. Catálogo e resumo da execução

`catalogo_bases.csv` registra os arquivos usados pelo pipeline, formato, camada, encoding, quantidade de registros e quantidade de colunas.

`resumo_execucao.json` registra:

- status da execução;
- data e hora em UTC;
- tamanho do entorno em metros;
- pessoas e famílias encontradas no CadÚnico;
- quantidade de arquivos tratados;
- bases submetidas ao recorte espacial.
