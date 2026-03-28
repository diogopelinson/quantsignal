# QuantSignal 📈

Pipeline completo de ranqueamento de ações globais com machine learning — do dado bruto ao deploy em produção na AWS.

Analisa mais de 120 ações dos mercados dos Estados Unidos, Brasil, Reino Unido e Japão. Calcula fatores quantitativos e usa um modelo LightGBM para ranquear as ações com maior potencial de valorização nas próximas semanas.

---

## API pública

A API está disponível publicamente por alguns dias para demonstração. Nenhuma instalação necessária — use direto pelo navegador ou terminal.

**URL base:**
```bash
http://afee7468164e34c6fae28ae59c006faf-235868092.us-east-1.elb.amazonaws.com
```

- API Desativada para Minimizar Custos de Infraestrutura.


> [!NOTE]
> **Observação de segurança**
>
> O **AWS Account ID** pode aparecer em algumas URLs públicas da infraestrutura (como Load Balancer e ECR), pois este é um projeto pessoal com deploy aberto para fins de demonstração.
>
> Isso não representa risco direto, pois:
> - Nenhuma credencial sensível é exposta
> - O acesso aos recursos é controlado via IAM
> - Apenas endpoints públicos necessários estão acessáveis
>
> Em um ambiente de produção real, boas práticas adicionais seriam aplicadas, como:
> - Uso de domínio customizado (ex: api.seuprojeto.com) para ocultar detalhes da infraestrutura
> - Proxy reverso (ex: API Gateway ou CloudFront)
> - Restrição de acesso a serviços internos (ECR, EKS) via rede privada
> - Remoção de identificadores sensíveis de documentação pública
>
> Essa abordagem aqui foi intencional para simplificar o acesso e demonstração do sistema.

### Endpoints

| Endpoint | Descrição |
|---|---|
| `GET /health` | Verifica se a API está no ar |
| `GET /signals?market=US&top_n=10` | Ranqueamento das ações mais promissoras |
| `GET /explain/{ticker}` | Explica o score de uma ação específica |
| `GET /model/info` | Versão e métricas do modelo em produção |

### Swagger UI

Como a API foi construída com **FastAPI**, a documentação interativa fica disponível automaticamente:

> [!IMPORTANT]
> Documentação interativa disponível em:  
> [Swagger UI](http://afee7468164e34c6fae28ae59c006faf-235868092.us-east-1.elb.amazonaws.com/docs)

Nela é possível:
- Testar os endpoints diretamente no navegador
- Visualizar os schemas de request e response
- Entender rapidamente como integrar a API em outros sistemas

### Parâmetros do `/signals`

| Parâmetro | Opções | Padrão |
|---|---|---|
| `market` | `US`, `BR`, `UK`, `JP` | `US` |
| `top_n` | 5 a 100 | 20 |

### Exemplos

```bash
# Top 5 ações americanas
curl "http://afee7468164e34c6fae28ae59c006faf-235868092.us-east-1.elb.amazonaws.com/signals?market=US&top_n=5"

# Top 10 ações brasileiras
curl "http://afee7468164e34c6fae28ae59c006faf-235868092.us-east-1.elb.amazonaws.com/signals?market=BR&top_n=10"

# Por que a NVDA está no ranqueamento?
curl "http://afee7468164e34c6fae28ae59c006faf-235868092.us-east-1.elb.amazonaws.com/explain/NVDA"

# Informações do modelo
curl "http://afee7468164e34c6fae28ae59c006faf-235868092.us-east-1.elb.amazonaws.com/model/info"
```

### Exemplo de resposta — `/signals`

```json
{
  "signals": [
    { "ticker": "ORCL", "score": 5.07, "rank": 1, "market": "US" },
    { "ticker": "NOW",  "score": 5.07, "rank": 2, "market": "US" },
    { "ticker": "INTU", "score": 5.07, "rank": 3, "market": "US" }
  ],
  "model_version": "1",
  "market": "US",
  "top_n": 5,
  "last_trained": "2026-03-25 03:35"
}
```

### Exemplo de resposta — `/explain/NVDA`

```json
{
  "ticker": "NVDA",
  "score": -5.36,
  "contributions": [
    { "feature": "momentum_1m",  "value": -0.47, "contribution": -3.17 },
    { "feature": "volume_trend", "value": -0.39, "contribution":  0.32 },
    { "feature": "momentum_3m",  "value": -0.05, "contribution":  0.28 }
  ],
  "summary": "Score driven mainly by momentum_1m (contribution: -3.168)"
}
```

---

## Como funciona

```text
Yahoo Finance (dados ao vivo — 120+ ações)
        ↓
Cálculo de fatores quantitativos
  momentum_1m / 3m / 6m / 12m
  volatilidade_1m / 3m
  tendência de volume
  posição vs máxima/mínima do ano
        ↓
Normalização cross-sectional (z-score)
        ↓
LightGBM LambdaRank
  aprende quais fatores precedem bons retornos
        ↓
Ranqueamento das ações (score de alfa esperado)
        ↓
FastAPI → AWS EKS → Load Balancer público
```

O modelo é **retreinado automaticamente toda segunda-feira** via GitHub Actions.

---

## Casos de uso

Este projeto foi pensado para aplicações financeiras reais, e não apenas para experimentação:

- **Estratégias de investimento quantitativo** — identificar ações com maior potencial usando ranqueamento orientado por dados
- **Apoio à alocação de portfólio** — ajudar na seleção de ativos com base em alfa esperado
- **Automação de triagem de mercado** — substituir filtros manuais por ranqueamento escalável com ML

> Esta API está temporariamente pública para demonstração e mostra um pipeline de machine learning em nível de produção.

---

## Testes

O projeto inclui testes automatizados para garantir confiabilidade nos componentes principais.

Execute os testes com:

```bash
pytest tests/ -v
```

A cobertura inclui:
- Lógica de engenharia de features
- Pipeline de ingestão de dados

Isso ajuda a manter consistência entre treinamento e inferência ao longo do tempo.

---

## Por que este projeto é diferente

Este não é um projeto comum de ML — ele foca em implantação real e otimização de ranqueamento:

- **Abordagem learning-to-rank (LightGBM LambdaRank)** em vez de regressão tradicional
- **Normalização cross-market de features** para comparação entre os mercados US, BR, UK e JP
- **Pipeline automatizado de retreinamento** com atualizações agendadas via CI/CD
- **Estrutura end-to-end em produção** (dados → modelo → API → deploy em cloud)

O objetivo é simular como modelos quantitativos são realmente construídos e operados em produção.

---

## Stack tecnológica

| Camada | Tecnologia |
|---|---|
| API | FastAPI + Uvicorn |
| ML | LightGBM (LambdaRank) + SHAP |
| Experiment tracking | MLFlow |
| Dados | Yahoo Finance (yfinance) |
| Qualidade de dados | Great Expectations |
| Container | Docker |
| Orquestração | Kubernetes (AWS EKS) |
| Infraestrutura como código | Terraform |
| Cloud | AWS |
| Registry de imagens | AWS ECR |
| CI/CD | GitHub Actions |

---

## Rodando localmente

### Pré-requisitos

- Python 3.11+
- Docker Desktop
- Git

### Passo a passo

**1. Clone o repositório**
```bash
git clone https://github.com/diogopelinson/quantsignal.git
cd quantsignal
```

**2. Crie e ative um ambiente virtual**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -e ".[dev]"
```

**4. Configure as variáveis de ambiente**
```bash
cp .env.example .env
```

Abra o `.env` e preencha:

```env
MLFLOW_TRACKING_URI=http://localhost:5000
```

**5. Suba o MLFlow**
```bash
docker compose up mlflow -d
```

Acesse `http://localhost:5000` para ver a interface do MLFlow.

**6. Treine o modelo**
```bash
python pipeline/train.py
```

Aguarde finalizar — vai aparecer `Created version '1' of model 'quantsignal-ranker'`.

**7. Suba a API**
```bash
uvicorn app.main:app --reload --port 8000
```

**8. Teste**
```bash
curl http://localhost:8000/health

curl "http://localhost:8000/signals?market=US&top_n=5"

curl http://localhost:8000/explain/NVDA
```

---

## Rodando com Docker Compose

```bash
# Sobe MLFlow + API juntos
docker compose up --build

# Treina o modelo (necessário na primeira vez)
docker compose run --rm app python pipeline/train.py

# Reinicia a API para carregar o modelo
docker compose restart app
```

---

## Estrutura do projeto

```text
quantsignal/
├── app/
│   ├── main.py              # ponto de entrada FastAPI
│   ├── schemas.py           # modelos Pydantic
│   └── routers/
│       ├── signals.py       # GET /signals
│       ├── explain.py       # GET /explain/{ticker}
│       └── model_info.py    # GET /model/info
├── pipeline/
│   ├── ingest.py            # busca dados do Yahoo Finance
│   ├── features.py          # cálculo de fatores quantitativos
│   ├── train.py             # treinamento + tracking no MLFlow
│   ├── validate.py          # validação de dados
│   └── promote.py           # promoção de modelo no registry
├── infra/
│   └── terraform/
│       ├── main.tf          # ECR
│       ├── vpc.tf           # VPC + subnets
│       ├── eks.tf           # cluster EKS
│       ├── variables.tf     # variáveis
│       ├── outputs.tf       # outputs
│       └── provider.tf      # provider AWS
├── k8s/
│   ├── app-deployment.yaml
│   ├── app-service.yaml
│   ├── mlflow-deployment.yaml
│   ├── mlflow-service.yaml
│   └── configmap.yaml
├── tests/
│   ├── test_features.py
│   └── test_ingest.py
├── utils/
│   └── wrapper.py
├── .github/
│   └── workflows/
│       ├── ci.yml           # lint + testes em todo PR
│       ├── cd.yml           # build → ECR → deploy EKS
│       └── retrain.yml      # retreinamento semanal
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Infraestrutura AWS

Toda a infraestrutura é provisionada via Terraform.

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

Recursos criados:
- **ECR** — repositório privado de imagens Docker
- **VPC** — rede isolada com subnets públicas e privadas
- **NAT Gateway** — acesso à internet para os nodes privados
- **EKS Cluster** — Kubernetes gerenciado pela AWS
- **Node Group** — instâncias EC2 t3.small
- **IAM Roles** — permissões para cluster e nodes

### Observação de segurança

O **AWS Account ID** aparece em URLs públicas da infraestrutura, como o ECR e o Load Balancer. Isso não expõe credenciais nem acesso privilegiado por si só, mas foi documentado aqui por transparência sobre a arquitetura publicada.

Para destruir toda a infraestrutura:

```bash
terraform destroy
```

---

## CI/CD

Todo push na branch `master` dispara automaticamente:

1. **CI** — lint com Ruff + testes com pytest
2. **CD** — build da imagem Docker → push para o ECR → deploy no EKS

O retreinamento acontece automaticamente toda segunda-feira às 6h UTC.

---

## Autor

Diogo Moraes — [LinkedIn](https://linkedin.com/in/diogopelinsonmoraes) · [GitHub](https://github.com/diogopelinson)
