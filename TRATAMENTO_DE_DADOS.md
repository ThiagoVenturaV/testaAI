# Tratamento de dados — Comunidade do Pilar

## 1. O que mudou

O projeto deixou de tratar as bases diretamente dentro do dashboard. O fluxo oficial agora é executado por `pipeline_dados.py`, que valida os arquivos, corrige tipos e codificação, cria recortes territoriais, calcula indicadores rastreáveis e grava produtos prontos para consumo.

O dashboard `pilar_dashboard.py` passou a utilizar apenas essas saídas processadas. O dashboard PRIME e seus eventos simulados não fazem parte do novo fluxo.

As principais mudanças foram:

1. organização dos dados em camadas;
2. leitura com detecção de codificação e saída padronizada em UTF-8;
3. validação de colunas obrigatórias e relatório de qualidade;
4. recorte do CadÚnico pela unidade de saúde do Pilar, sem fallback posicional;
5. recorte geográfico da ZEIS e de seu entorno de 500 metros;
6. indicadores calculados a partir das bases, com fonte e fórmula;
7. separação entre dados brutos, tratados, recortes e indicadores;
8. filtros analíticos no dashboard territorial;
9. catálogo das bases e resumo de cada execução;
10. retirada de dados simulados do fluxo territorial.

Conforme decisão do projeto, os microdados do CadÚnico continuam disponíveis no explorador e para download no dashboard. Não foi implementada anonimização ou restrição de visualização.

## 2. Arquitetura do novo fluxo

```text
Fontes_Summerjob/                  Camada bruta: arquivos originais preservados
        |
        v
pipeline_dados.py                  Validação, limpeza, recorte e indicadores
        |
        +-- dados/02_tratados/     CSVs padronizados em UTF-8
        +-- dados/03_recortes/     Pilar, ZEIS e entorno de 500 m
        `-- dados/04_indicadores/  KPIs, qualidade, catálogo e execução
                                           |
                                           v
                                pilar_dashboard.py
```

Não foi criada uma cópia em `dados/01_brutos`, pois `Fontes_Summerjob` já desempenha essa função. Isso evita duplicar centenas de megabytes sem necessidade.

## 3. Como executar

Na raiz de `testaAI`:

```powershell
pip install -r requirements.txt
python pipeline_dados.py
streamlit run pilar_dashboard.py
```

Sempre que um arquivo de `Fontes_Summerjob` for atualizado, o pipeline deve ser executado novamente antes do dashboard.

## 4. Leitura e codificação

### Antes

Os CSVs eram forçados para `latin1`. Algumas bases são UTF-8, o que produzia textos como `PraÃ§a` e podia dividir uma mesma categoria em grafias diferentes.

### Agora

Cada CSV é testado, nesta ordem:

1. `utf-8-sig`;
2. `utf-8`;
3. `latin1`.

O encoding aceito é registrado no catálogo. Todos os CSVs processados são gravados como `UTF-8-SIG`, facilitando a abertura correta tanto em Python como no Excel.

Uma função de normalização remove acentos, converte para maiúsculas, elimina espaços repetidos e cria colunas auxiliares, como `bairro_normalizado`. A coluna original é preservada.

### Motivo e consequência

- **Motivo:** impedir filtros e agrupamentos incorretos causados por codificação ou variações de texto.
- **Consequência positiva:** categorias consistentes e arquivos legíveis em diferentes programas.
- **Cuidado:** a normalização serve para comparação; o texto original continua sendo a referência de apresentação.

## 5. Validação de schema e qualidade

O pipeline define campos obrigatórios para cada base usada. Se um campo essencial desaparecer, a execução é interrompida com uma mensagem explícita. Isso substitui comportamentos silenciosos que poderiam manter o dashboard funcionando com dados incorretos.

Para cada CSV são registrados:

- arquivo e encoding detectado;
- total de registros e colunas;
- linhas integralmente duplicadas;
- quantidade e percentual de células nulas;
- status de qualidade.

O resultado é salvo em:

```text
dados/04_indicadores/relatorio_qualidade.csv
```

### Motivo e consequência

- **Motivo:** detectar mudanças nas fontes antes da visualização.
- **Consequência positiva:** erros passam a ser rastreáveis e auditáveis.
- **Consequência operacional:** uma mudança incompatível de schema bloqueará o pipeline até o código ser ajustado.

## 6. Conversões e padronizações

Os campos numéricos com vírgula decimal são convertidos para ponto e processados com `pd.to_numeric(errors="coerce")`. Valores impossíveis de converter tornam-se nulos e aparecem no relatório de qualidade.

Conversões implementadas:

| Base | Campos derivados |
|---|---|
| Praças | `area_m2`, `bairro_normalizado` |
| Ciclovias | `extensao_km`, `ano_inauguracao` |
| Urbanismo tático | `metragem_m` |
| Logradouros | `bairro_normalizado` |
| Wi-Fi | `bairro_normalizado` |
| CadÚnico | ano, raça/cor, sexo, idade, escolaridade, benefício, deficiência, situação de rua e rendas numéricas |

## 7. Tratamento do CadÚnico

### Recorte territorial

O recorte usa exclusivamente a coluna `d.nom_estab_assist_saude_fam` e exige a palavra completa `PILAR`. Na base atual, isso identifica:

```text
US 278 USF NOSSA SRA DO PILAR BAIRRO DO RECIFE
```

O resultado observado na inspeção foi de 145 pessoas pertencentes a 73 famílias.

O comportamento anterior que selecionava as primeiras 145 linhas quando o Pilar não era encontrado foi removido. Se a unidade não for localizada, o pipeline falha.

### Variáveis categóricas derivadas

Os códigos são traduzidos para rótulos compreensíveis:

- raça/cor: Branca, Preta, Amarela, Parda e Indígena;
- sexo: Masculino e Feminino;
- faixa etária;
- escolaridade;
- Bolsa Família;
- pessoa com deficiência;
- situação de rua.

O ano é extraído de `dat_atualizacao`. Renda per capita, renda familiar e despesa com alimentação são convertidas em números.

### Família versus pessoa

A base possui uma linha por pessoa e repete dados familiares. Indicadores de pessoas usam todas as linhas. Indicadores familiares removem repetições por `cod_familiar` antes do cálculo. Isso evita contar uma família várias vezes por causa de seus membros.

### Motivo e consequência

- **Motivo:** eliminar uma seleção arbitrária e diferenciar corretamente unidade pessoa e unidade família.
- **Consequência positiva:** os indicadores passam a corresponder à unidade assistencial do Pilar.
- **Possível mudança:** totais e médias podem divergir do dashboard antigo porque agora as fórmulas são executadas sobre os campos reais.
- **Limitação:** o vínculo com a USF caracteriza a população atendida pela unidade; não prova residência dentro da poligonal da ZEIS.

## 8. Recorte geoespacial

O filtro por palavras foi substituído por operações geográficas para as bases que possuem coordenadas.

### Processo

1. a ZEIS cujo `NMNOME` contém a palavra completa “Pilar” é selecionada;
2. geometrias inválidas são reparadas;
3. pontos e polígono são convertidos para `EPSG:31985`, adequado a medições métricas na região;
4. cria-se um buffer de 500 metros;
5. cada ponto recebe uma classificação:

   - `ZEIS Pilar`;
   - `Entorno até 500 m`;
   - `Fora do recorte`.

As coordenadas também passam por uma verificação de limites aproximados do Recife antes da criação dos pontos.

### Bases classificadas espacialmente

- pontos de Wi-Fi;
- parques e praças;
- intervenções de urbanismo tático.

Os recortes são gravados em CSV e GeoJSON em `dados/03_recortes`.

### Motivo e consequência

- **Motivo:** encontrar equipamentos pela localização real, não pelo texto do bairro ou nome.
- **Consequência positiva:** afirmações como “dentro da ZEIS” tornam-se reproduzíveis.
- **Possível mudança:** as quantidades podem ser diferentes das obtidas por busca textual.
- **Limitação:** registros sem coordenadas válidas não entram no recorte espacial e permanecem contabilizados apenas na camada tratada.

## 9. Logradouros e pavimentação

Como a base de logradouros utilizada não contém geometria, o recorte continua sendo feito pelo campo de bairro normalizado, exigindo valor igual a `RECIFE`.

O indicador de déficit soma registros classificados como:

- Via Não Pavimentada;
- Via Parcialmente Pavimentada.

Os valores fixos 3 e 4 usados anteriormente como fallback foram removidos. Se as categorias mudarem, o resultado refletirá os dados existentes e a mudança poderá ser detectada no relatório.

## 10. Indicadores rastreáveis

O arquivo `dados/04_indicadores/indicadores_territoriais.csv` possui uma linha por indicador e as colunas:

- `indicador`;
- `valor`;
- `unidade`;
- `territorio`;
- `formula`;
- `fonte`;
- `gerado_em_utc`.

São calculados:

- pessoas e famílias atendidas pela USF Pilar;
- percentual de pessoas pretas ou pardas;
- percentual de famílias beneficiárias do Bolsa Família;
- renda per capita média;
- renda familiar média;
- área da ZEIS Pilar;
- pontos de Wi-Fi dentro da ZEIS;
- pontos de Wi-Fi no entorno de 500 metros;
- vias com déficit no Bairro do Recife.

### Motivo e consequência

- **Motivo:** retirar percentuais e valores de renda digitados diretamente no dashboard.
- **Consequência positiva:** cada número possui fórmula, fonte e data de geração.
- **Possível mudança:** resultados anteriormente divulgados podem precisar de revisão quando não forem reproduzidos pelas bases.

## 11. Dashboard territorial

O novo `pilar_dashboard.py` lê somente as camadas processadas. Se elas não existirem, informa que o pipeline precisa ser executado.

### Filtros disponíveis

- raça/cor;
- ano de atualização cadastral;
- sexo;
- faixa etária;
- escolaridade;
- Bolsa Família;
- pessoa com deficiência;
- situação de rua;
- intervalo de renda per capita.

Os filtros atualizam:

- pessoas e famílias;
- percentual de população preta ou parda;
- percentual de famílias no Bolsa Família;
- renda per capita média;
- renda familiar média, calculada após remover repetições por `cod_familiar`;
- gráficos de raça/cor, ano, idade e escolaridade;
- tabela de microdados e download do recorte filtrado.

O território apresenta ainda mapa de equipamentos, área da ZEIS, Wi-Fi, pavimentação, indicadores e relatório de qualidade.

## 12. Dados reais e simulados

O `prime_dashboard.py` não é chamado pelo pipeline nem pelo dashboard territorial. Seus pilotos, eventos, usuários e séries temporais simuladas não entram em nenhum indicador oficial.

### Motivo e consequência

- **Motivo:** impedir que dados demonstrativos sejam confundidos com observações reais.
- **Consequência positiva:** o diagnóstico territorial contém apenas dados locais processados e indicadores identificados.
- **Estado do arquivo:** o código PRIME foi preservado como protótipo histórico, mas está fora do procedimento oficial.

## 13. Arquivos produzidos

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
│   ├── pracas_pilar_entorno.csv/.geojson
│   ├── urbanismo_pilar_entorno.csv/.geojson
│   ├── wifi_pilar_entorno.csv/.geojson
│   └── zeis_pilar.geojson
└── 04_indicadores/
    ├── catalogo_bases.csv
    ├── indicadores_territoriais.csv
    ├── relatorio_qualidade.csv
    └── resumo_execucao.json
```

## 14. Limitações restantes

1. O CadÚnico é recortado por unidade assistencial, não por endereço ou coordenada residencial.
2. Logradouros não possuem geometria na base utilizada.
3. O catálogo registra os arquivos usados pelo pipeline, não todas as 65 bases disponíveis.
4. Dados ausentes não são imputados; permanecem nulos para evitar criação artificial de informação.
5. O relatório identifica duplicatas, mas não as remove automaticamente, pois uma repetição aparente pode representar pessoas distintas ou registros válidos.
6. Os microdados do CadÚnico permanecem visíveis por decisão explícita deste projeto.

## 15. Efeito geral das mudanças

O tratamento anterior privilegiava velocidade de prototipação. O novo fluxo privilegia rastreabilidade, reprodutibilidade e precisão territorial. Como consequência, o projeto passa a falhar de forma explícita quando uma base essencial muda, e alguns números podem ser diferentes dos exibidos anteriormente. Essa mudança é intencional: um resultado ausente ou revisado é preferível a um indicador aparentemente válido produzido por fallback, texto aproximado ou valor fixo.
