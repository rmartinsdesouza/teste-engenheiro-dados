# Teste Engenheiro de Dados — Pipeline BigQuery

Este projeto implementa um pipeline de dados em 3 camadas (RAW → Curated → Analytics) no BigQuery, com scripts Python e um runner simples para executar tudo de ponta a ponta.

- Documentação técnica completa: veja `docs/README.md`
- Dicionário de dados: `docs/dicionario_dados.md`
- Otimizações e próximos passos: `docs/otimizacoes.md`
- Diagrama de arquitetura (Mermaid): `docs/diagrama_arquitetura.mmd`

## Arquitetura visual
![arquitetura](/docs/image.png)

[Arquitetura_em_pdf](docs/Arquitetura_de_Data_Lake_Python.pdf)

## Pré-requisitos

- Python 3.11+ (testado com 3.12)
- Projeto GCP com BigQuery habilitado
- Credenciais: arquivo `cred.json` na raiz (ou `GOOGLE_APPLICATION_CREDENTIALS` no ambiente)

## Instalação

```bash
python3 -m venv .venv-gcp
source .venv-gcp/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Como executar

### Rodar as etapas manualmente (RAW → Curated → Analytics):

```bash
# RAW
./.venv-gcp/bin/python scripts/clientes_raw.py
./.venv-gcp/bin/python scripts/analises_tributarias_raw.py
./.venv-gcp/bin/python scripts/notas_fiscais_raw.py
./.venv-gcp/bin/python scripts/tarefas_projetos_raw.py
./.venv-gcp/bin/python scripts/logs_sistema.py

# Curated
./.venv-gcp/bin/python scripts/clientes_curated.py
./.venv-gcp/bin/python scripts/analises_tributarias_curated.py
./.venv-gcp/bin/python scripts/notas_fiscais_curated.py
./.venv-gcp/bin/python scripts/logs_sistema_curated.py
./.venv-gcp/bin/python scripts/tarefas_projetos_curated.py

# Analytics
./.venv-gcp/bin/python scripts/resumo_clientes_tributos.py
./.venv-gcp/bin/python scripts/performance_projetos.py
```

### Rodar as etapas agendadas


## Estrutura de diretório e aquivos

```text
dados/                  # fontes CSV/TXT/JSON/XML/HTML
docs/                   # documentação técnica, dicionário, diagrama
scripts/                # scripts de ingestão, transformação e analytics
  run_all.py            # executa todos os fontes para analises
  utils_bq.py           # utilitários de IO BigQuery (ler/escrever DataFrame)
  utils_curated.py      # funções de limpeza/normalização
  *_raw.py              # cargas RAW para BigQuery
  *_curated.py          # limpezas/flatten e criação da camada curated
  resumo_* / performance_*  # tabelas analytics
```

# 🧭 Resumo Executivo

Este projeto foi desenvolvido com o objetivo de demonstrar pensamento crítico, visão arquitetural e boas práticas de engenharia de dados, aplicadas a um cenário de iniciação de projetos em uma empresa com potencial de expansão rápida.
Todas as decisões técnicas foram tomadas com base em experiências anteriores, melhores práticas do mercado e no contexto real de operação de times de dados, equilibrando eficiência, custo e escalabilidade.
A solução proposta entrega uma estrutura funcional, modular e aderente a padrões modernos de mercado (como arquitetura medalhão e uso do BigQuery) — com espaço planejado para evoluções estruturadas, sem comprometer a manutenção ou o crescimento futuro do ambiente.


## 🧩 Decisões Técnicas Justificadas  
Durante o desenvolvimento, foram consideradas múltiplas abordagens baseadas em **projetos e estudos anteriores**, sempre ponderando o **momento atual da empresa** — com um **time pequeno**, mas com **potencial de crescimento acelerado**.  

Reforça-se que **quanto maior o entendimento do negócio**, melhor é a capacidade do time de **propor soluções de dados alinhadas à estratégia corporativa**.

---

## ⚠️ Erros e Faltas  
O foco principal desta entrega foi **demonstrar pensamento crítico por meio do código**, apresentando uma **versão funcional**, ainda que **em estágio de testes**.  
Portanto, é natural que existam **pontos de melhoria**, os quais podem ser **identificados, classificados e resolvidos** em versões futuras.  

Em relação às entregas opcionais, a **ausência de alguns arquivos** — como o solicitado `pipeline_ingestao.py` — **impediria o funcionamento completo da programação funcional**, motivo pelo qual foi destacada a importância de sua presença na estrutura do projeto.

---

## 🏗️ Arquitetura Medalhão  
Como solicitado, foi adotada a **arquitetura medalhão (Bronze, Silver e Gold)**, reconhecida como uma das **melhores práticas atuais para tratamento e organização de dados**.  

Seguindo uma recomendação acertada, foi utilizado o **BigQuery**, recurso em nuvem do Google, **via API oficial da ferramenta**.  
Essa decisão **evita riscos de vendor lock-in** e garante **sustentabilidade e flexibilidade tecnológica** para futuras evoluções.  

No modelo de ingestão:  
- O formato **JSON semi-estruturado** foi o único armazenado em sua forma nativa na camada *raw*;  
- Embora o BigQuery seja capaz de inferir o *schema* automaticamente, os **demais formatos tabulares foram salvos diretamente como tabelas**;  
- Essa abordagem **facilita o acesso aos dados na camada *raw*** e **reduz custos de reprocessamento e duplicidade**.

---

## 🧠 Programação Funcional  
Foi escolhida a abordagem de **programação baseada em funções**, que traz diversas vantagens:  

- ♻️ **Reaproveitamento de código**  
- 🧩 **Manutenção centralizada e simplificada**  
- ⚡ **Maior agilidade nas entregas**  

Como exemplo, há **scripts com cerca de 15 linhas** capazes de executar **etapas completas de processamento**, demonstrando **eficiência e clareza** no desenvolvimento.

---

## ✅ Boas Práticas  
Foram criadas **rotinas padronizadas**, contemplando:  

- 🐍 **Nomes de colunas** no padrão *snake_case* em todas as camadas;  
- ⚙️ **Tratamento de valores nulos**, tipagens e chaves primárias;  
- 🪵 **Rotina de logs robusta**, com **rotação de arquivos** e **classificação de mensagens**.  

As **boas práticas do padrão PEP8** foram consideradas, mas aplicadas de forma **flexível**, visando **equilíbrio entre padronização e produtividade**, especialmente em **times enxutos**.  

As **rotinas automatizadas de teste** também podem reforçar esses padrões, realizando:  
- 🔠 Ordenação automática de *imports* em ordem alfabética;  
- 🧾 Quebra de linhas com mais de 70 caracteres;  
- 🔒 Validação de segurança (como **detecção de senhas expostas** no código-fonte);  
- 🧪 Outras verificações automáticas de **qualidade e segurança**.

---

## 📊 Utilização de DataFrames  
Foi priorizada a utilização de **tabelas baseadas em DataFrames** (Pandas ou BigQuery), pois essas estruturas:  
- **Simplificam o tratamento de dados**;  
- Mantêm **compatibilidade com consultas SQL**;  
- Garantem **flexibilidade** e **eficiência** tanto para **processamento em Python** quanto para **análises declarativas**.

---

## 🚀 Próximos Passos e Melhorias Sugeridas  

- 🐳 **Definir um ambiente padrão de desenvolvimento** utilizando containers **Docker**, **Terraform** ou ambientes colaborativos como **Google Colab**;  
- 🧱 **Refatorar o código-fonte** aplicando **Programação Orientada a Objetos (POO)** para maior **modularização** e **escalabilidade**;  
- 🔐 **Ajustar permissões de acesso** conforme áreas e perfis, seguindo o **Princípio do Menor Privilégio (Principle of Least Privilege)**;  
- 🧪 **Implementar rotinas automatizadas de testes**, garantindo **qualidade**, **rastreabilidade** e **estabilidade contínua** nas entregas.

---
