# Documentação do tratamento de dados

## 1. Objetivo e escopo

Esta documentação descreve como os dados da pasta `Fontes_Summerjob` são carregados, selecionados, transformados e utilizados pelos scripts deste repositório.

O fluxo foi reconstruído a partir do código-fonte existente. O projeto **não possui uma única rotina ETL que produza versões permanentemente limpas das 65 bases**. Em vez disso, os arquivos originais são preservados e o tratamento ocorre em memória, durante a execução dos scripts de exploração e dos dashboards.

## 2. Visão geral do fluxo

```text
Fontes_Summerjob (CSV, GeoJSON, JSON e SHP)
        |
        +-- scripts scratch_*: inspeção inicial e descoberta de campos
        |
        +-- extract_pilar_rich.py: seleção, conversão, agregação e exportação
        |       `-- pilar_rich_data.json
        |
        +-- scratch_pilar.py: recorte textual do Pilar e entorno
        |       `-- pilar_output.json
        |
        +-- pilar_dashboard.py: tratamento em memória e visualização territorial
        |
        `-- prime_dashboard.py: dados reais de contexto + eventos simulados
```

Não foram encontrados `merge` ou `join` entre bases. A integração ocorre no nível analítico: indicadores de arquivos diferentes são apresentados juntos, mas as linhas não são cruzadas por uma chave comum.

## 3. Organização e identificação das bases

As bases ficam em `Fontes_Summerjob`. Os nomes originais possuíam o padrão:

```text
resources_<UUID>_<descricao>.<extensao>
```

Para facilitar a identificação, o prefixo `resources_` e o UUID foram removidos, mantendo a descrição e a extensão. Dois dicionários originalmente homônimos foram diferenciados pelo conteúdo:

- `dicionario-trechos-de-logradouros.json`
- `dicionario-logradouros-por-face-de-quadra.json`

Os scripts encontram as bases com `Path.glob("*parte-do-nome.extensao")`. Por isso, a retirada dos UUIDs não alterou a forma de localização dos arquivos.

## 4. Leitura e padronização técnica

### Arquivos CSV

Os CSVs são lidos com Pandas usando, em geral:

```python
pd.read_csv(arquivo, sep=None, engine="python", encoding="latin1")
```

Isso significa:

- `sep=None`: o separador é inferido automaticamente;
- `engine="python"`: permite a detecção automática do separador;
- `encoding="latin1"`: trata as bases fornecidas com codificação Latin-1.

Não existe padronização global dos nomes das colunas. Cada script verifica os nomes esperados ou procura alternativas, como `rpa`/`RPA`, `bairro`/`Bairro` e `extensao`/`Extensão`.

### Dados geoespaciais

GeoJSON e Shapefile são lidos com `geopandas.read_file`. Quando apenas os atributos são necessários, a coluna `geometry` é removida e o objeto é convertido em `DataFrame`:

```python
pd.DataFrame(gdf.drop(columns=["geometry"]))
```

O código atual não reprojeta coordenadas, não valida geometrias e não realiza interseção espacial. Portanto, afirmações como “dentro da poligonal” não foram calculadas por `spatial join` nos scripts inspecionados; os recortes implementados são predominantemente textuais.

### Conversão de tipos

As conversões numéricas identificadas são:

- `AREA_HA` das ZEIS: `pd.to_numeric(..., errors="coerce")`;
- `area` de parques e praças: `pd.to_numeric(..., errors="coerce")`;
- extensão cicloviária, em script exploratório: conversão de vírgula para ponto e depois `float`.

Com `errors="coerce"`, valores inválidos tornam-se `NaN`. Antes de rankings, campos nulos relevantes são descartados com `dropna()`.

## 5. Recortes territoriais

Os recortes não utilizam uma chave territorial padronizada. Eles são feitos por busca textual, normalmente sem diferenciar maiúsculas e minúsculas e ignorando nulos.

### Comunidade do Pilar e entorno

São usados termos como:

- `pilar`;
- `recife` ou valor exato `RECIFE` no campo de bairro;
- `brum`;
- `apolo`.

Exemplos de implementação:

```python
serie.str.lower().str.contains("pilar", na=False)
serie.str.contains("PILAR", case=False, na=False)
df[df["nomeBairro"].str.upper().str.strip() == "RECIFE"]
```

No `scratch_pilar.py`, algumas buscas examinam a representação textual da linha inteira. Isso amplia a recuperação, mas pode gerar falsos positivos se o termo aparecer em um campo sem relação territorial.

### CadÚnico 2023

No `pilar_dashboard.py`, o processo é:

1. localizar colunas cujo nome contenha `estab_assist`, `centro_assist` ou `nom_`;
2. percorrer essas colunas;
3. selecionar a primeira que contenha o texto `PILAR` em alguma linha;
4. usar todas as linhas correspondentes dessa coluna;
5. se nada for localizado, usar as primeiras 145 linhas como fallback.

O arquivo completo é carregado em memória. Não há anonimização, deduplicação ou validação explícita de identificadores pessoais no código. Por se tratar de dado social potencialmente sensível, o acesso e a exposição de microdados devem ser revisados antes de publicação.

## 6. Tratamentos por conjunto de dados

| Tema/base | Tratamento implementado | Resultado utilizado |
|---|---|---|
| ZEIS | remove geometria para análise tabular; converte `AREA_HA`; filtra `NMNOME` por “pilar”; remove nulos; ordena por área | total, área média, ZEIS Pilar e ranking das 20 maiores |
| Parques e praças | converte `area`; agrupa e soma por `nome_bairro`; calcula média; conta registros; filtra bairro contendo “recife” | área total/média, ranking de bairros e equipamentos do Bairro do Recife |
| Malha cicloviária | conta categorias com `value_counts`; filtra `bairros` contendo “recife”; seleciona campos de rota | totais, tipologias, extensão e rotas do entorno |
| Wi-Fi Conecta Recife | conta pontos por bairro; filtra `bairro` contendo “recife” | total, ranking por bairro e pontos do recorte |
| Urbanismo tático | conta por ano, tipo e bairro; filtra bairro/linha por Recife, Pilar, Brum ou Apolo | intervenções do entorno e distribuições categóricas |
| Bairros e RPAs | conta bairros por RPA; seleciona registros com `rpa == 1` | lista de bairros da RPA 1 |
| Logradouros | filtra `nomeBairro`; conta `desc_indica_pavimentacao` | 54 registros do Bairro do Recife e situação de pavimentação |
| Microrregiões | remove geometria e coleta colunas/amostra | inspeção exploratória |
| ZEPH | busca Pilar/Recife no conteúdo textual da linha e remove a geometria da exportação | registros de patrimônio histórico do entorno |
| Prédios públicos e pontes | leitura, contagem e amostra de atributos | exploração inicial |

## 7. Agregações e indicadores

As operações mais frequentes são:

- `len(df)` para total de registros;
- `value_counts()` para frequências de categorias;
- `groupby(...).sum()` para área de praças por bairro;
- `mean()` e `sum()` para áreas;
- `sort_values()` e `head()` para rankings;
- `to_dict(orient="records")` para serialização em JSON.

Para pavimentação, o dashboard soma as categorias “Via Não Pavimentada” e “Via Parcialmente Pavimentada”. Caso essas chaves não sejam encontradas exatamente, utiliza os fallbacks 3 e 4.

## 8. Arquivos gerados

### `analysis_output.json`

Gerado por `scratch_analysis2.py`. Contém resultados exploratórios de pontes, ZEIS, urbanismo tático, Programa Tá Aprumado e malha cicloviária.

### `pilar_output.json`

Gerado por `scratch_pilar.py`. Reúne registros encontrados por buscas textuais relacionadas ao Pilar, Bairro do Recife e entorno.

### `pilar_rich_data.json`

Gerado por `extract_pilar_rich.py`. Consolida métricas e amostras de ZEIS, praças, ciclovias, Wi-Fi, urbanismo tático, microrregiões, RPAs e logradouros.

Os JSONs usam UTF-8, indentação de dois espaços e `ensure_ascii=False`. No arquivo rico, `default=str` converte tipos não serializáveis para texto.

## 9. Uso nos dashboards

### `pilar_dashboard.py`

Carrega dados reais em memória e aplica os filtros descritos acima. O carregamento usa cache do Streamlit (`@st.cache_data`). Parte dos indicadores exibidos é fixa no código, incluindo percentuais e valores de renda, gasto alimentar e dados habitacionais. Portanto, nem todos os KPIs apresentados são recalculados diretamente a partir das bases em cada execução.

### `prime_dashboard.py`

Usa bases reais para contextualização territorial, praças, ZEIS e pavimentação. Entretanto, os pilotos, eventos, usuários, satisfação, séries temporais e classificações exibidos são simulações geradas no próprio código, inclusive com valores aleatórios. Esses dados não devem ser interpretados como observações reais.

## 10. Validação e tratamento de erros

Os scripts exploratórios e de extração envolvem cada conjunto em `try/except`. Em caso de falha, a mensagem é gravada no resultado com chaves como `err_zeis`, `err_wifi` ou `err_log`, permitindo que as demais bases continuem sendo processadas.

As validações existentes são principalmente:

- teste de existência da pasta local;
- busca do primeiro arquivo que corresponda ao padrão (`glob(...)[0]`);
- verificação de existência de colunas antes de alguns cálculos;
- descarte de nulos em rankings;
- conversão tolerante de números inválidos.

Não foram identificados testes automatizados, validação de schema, controle de duplicatas, auditoria de valores extremos, conferência de CRS ou comparação automática entre quantidade de entrada e saída.

## 11. Limitações e cuidados de interpretação

1. **Recorte textual:** buscar “Recife” ou “Pilar” não equivale a uma interseção geográfica com a poligonal da ZEIS.
2. **Fallback do CadÚnico:** as primeiras 145 linhas não são uma substituição metodologicamente segura para registros do Pilar.
3. **Indicadores fixos:** alguns KPIs do dashboard foram digitados manualmente e não têm cálculo rastreável nas bases locais.
4. **Codificação:** há sinais de texto com caracteres corrompidos em alguns artefatos gerados; a cadeia Latin-1 → UTF-8 precisa ser validada.
5. **Ausência de integração por chave:** as bases são analisadas lado a lado, sem vínculo registro a registro.
6. **Dados sensíveis:** a exibição de microdados do CadÚnico exige avaliação de privacidade, necessidade e base legal.
7. **Dados simulados:** o dashboard PRIME mistura contexto real com eventos fictícios para demonstração.
8. **Reprodutibilidade parcial:** alguns scripts `scratch_*` ainda apontam para um caminho absoluto de outro computador, enquanto `extract_pilar_rich.py` e os dashboards usam a pasta local.

## 12. Como reproduzir o tratamento principal

Na raiz do projeto:

```powershell
python extract_pilar_rich.py
streamlit run pilar_dashboard.py
```

O primeiro comando recria `pilar_rich_data.json`. O segundo carrega as bases, aplica os filtros em memória e abre o dashboard.

Antes de uma publicação ou decisão de política pública, recomenda-se substituir os filtros textuais por operações espaciais, eliminar fallbacks silenciosos, calcular todos os KPIs a partir de fontes rastreáveis e implementar testes de qualidade e privacidade.

