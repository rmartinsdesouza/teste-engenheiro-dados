# Dicionário de Dados

Este documento descreve os principais conjuntos de dados nas camadas RAW, Curated e Analytics do BigQuery.

Observação: tipos podem ser ajustados automaticamente pelo BigQuery (`autodetect`). Nas camadas Curated e Analytics buscamos manter padronização e coerção de tipos.

## RAW (psa_raw)

- clientes
  - id_cliente (STRING)
  - razao_social (STRING)
  - cnpj (STRING)
  - porte_empresa (STRING)
  - setor (STRING)
  - cidade (STRING)
  - estado (STRING)
  - data_cadastro (STRING/DATE)

- analises_tributarias
  - id_analise (STRING)
  - cliente_id (STRING)
  - tipo_tributo (STRING)
  - periodo_analise (STRING)
  - valor_identificado (FLOAT)
  - observacoes (STRING)

- tarefas_projetos (JSON bruto por linha)
  - projetos (`ARRAY<STRUCT>`)
    - id_projeto, nome_projeto, cliente_id, responsavel, data_inicio, data_prevista_fim, status, valor_projeto, horas_totais_estimadas, horas_totais_realizadas
  - tarefas (`ARRAY<STRUCT>`): id_tarefa, descricao, status_tarefa, responsavel_tarefa, data_inicio, data_prevista_fim, horas_estimadas, horas_realizadas

- logs_sistema
  - id_log (STRING)
  - timestamp (STRING/DATETIME)
  - usuario (STRING)
  - acao (STRING)
  - entidade_afetada (STRING)
  - resultado (STRING)
  - ip (STRING)

- notas_fiscais / notas_fiscais_raw
  - Dependendo do modo de ingestão, pode ser:
    - tabela com colunas (NumeroNota, DataEmissao, ClienteID, ValorServico, Impostos, ValorTotal, Itens)
    - OU arquivo bruto em coluna única `raw`

## Curated (psa_curated)

- clientes
  - id_cliente (STRING) — chave
  - razao_social (STRING)
  - cnpj (STRING, dígitos apenas)
  - porte_empresa (STRING)
  - setor (STRING)
  - cidade (STRING)
  - estado (STRING)
  - data_cadastro (DATE)

- analises_tributarias
  - id_analise (STRING) — chave
  - cliente_id (STRING)
  - tipo_tributo (STRING)
  - periodo_analise (STRING)
  - valor_identificado (FLOAT)
  - observacoes (STRING)

- tarefas_projetos (achata tarefas, duplicando metadados do projeto)
  - projeto_id (STRING)
  - projeto_nome (STRING)
  - projeto_cliente_id (STRING)
  - projeto_responsavel (STRING)
  - projeto_status (STRING)
  - projeto_data_inicio (DATE/DATETIME)
  - projeto_data_prevista_fim (DATE/DATETIME)
  - projeto_valor (FLOAT/NUMERIC)
  - projeto_horas_totais_estimadas (FLOAT)
  - projeto_horas_totais_realizadas (FLOAT)
  - tarefa_id (STRING)
  - tarefa_descricao (STRING)
  - tarefa_status (STRING)
  - tarefa_responsavel (STRING)
  - tarefa_data_inicio (DATE/DATETIME)
  - tarefa_data_prevista_fim (DATE/DATETIME)
  - tarefa_horas_estimadas (FLOAT)
  - tarefa_horas_realizadas (FLOAT)

- logs_sistema
  - id_log (STRING) — chave
  - timestamp (DATETIME)
  - usuario (STRING)
  - acao (STRING)
  - entidade_afetada (STRING)
  - resultado (STRING)
  - ip (STRING)

- notas_fiscais
  - numeronota (STRING)
  - dataemissao (DATE)
  - clienteid (STRING)
  - valorservico (FLOAT)
  - impostos (FLOAT/STRING padronizada)
  - valortotal (FLOAT)
  - itens (STRING)

## Analytics (psa_analytics)

- resumo_clientes_tributos
  - cliente_id (STRING)
  - razao_social (STRING)
  - cnpj (STRING)
  - porte_empresa (STRING)
  - setor (STRING)
  - cidade (STRING)
  - estado (STRING)
  - tipo_tributo (STRING)
  - qtd_analises (INTEGER)
  - valor_total_identificado (FLOAT)
  - valor_medio_identificado (FLOAT)

- performance_projetos
  - projeto_id (STRING)
  - projeto_nome (STRING) — se presente na curated
  - projeto_cliente_id (STRING)
  - projeto_responsavel (STRING)
  - projeto_status (STRING)
  - projeto_data_inicio (DATE/DATETIME)
  - projeto_data_prevista_fim (DATE/DATETIME)
  - qtd_tarefas (INTEGER)
  - horas_estimadas_total (FLOAT)
  - horas_realizadas_total (FLOAT)
  - horas_saldo (FLOAT)
  - pct_execucao (FLOAT: 0–1)
  - tarefas_status_`<valor>` (INTEGER) — colunas geradas dinamicamente por pivot (ex.: tarefas_status_concluida, tarefas_status_em_andamento, tarefas_status_pendente)

## Observações gerais

- Nomes de colunas padronizados para snake_case na camada Curated
- Datas parseadas quando possível; valores não parseáveis permanecem como STRING
- Chaves nulas são descartadas em Curated para estabilidade das análises
- Tipos podem variar por `autodetect`; ajustar schema explícito é um próximo passo recomendado
