# QuantSignal 📈

Pipeline completo de ranking de ações globais com machine learning — do dado bruto ao deploy em produção na AWS.

Analisa mais de 120 ações dos mercados dos EUA, Brasil, Reino Unido e Japão. Calcula fatores quantitativos e usa um modelo LightGBM para ranquear as ações com maior potencial de valorização nas próximas semanas.

---

## API pública

A API está disponível publicamente por alguns dias. Nenhuma instalação necessária — use direto pelo browser ou terminal.

**URL base:**
```
http://afee7468164e34c6fae28ae59c006faf-235868092.us-east-1.elb.amazonaws.com
```

### Endpoints

| Endpoint | Descrição |
|---|---|
| `GET /health` | Verifica se a API está no ar |
| `GET /signals?market=US&top_n=10` | Ranking das ações mais promissoras |
| `GET /explain/{ticker}` | Explica o score de uma ação específica |
| `GET /model/info` | Versão e métricas do modelo em produção |

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

# Por que a NVDA está no ranking?
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

```
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
Ranking das ações (score de alfa esperado)
        ↓
FastAPI → AWS EKS → Load Balancer público
```

O modelo é **retreinado automaticamente toda segunda-feira** via GitHub Actions.

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
| Cloud | AWS
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
```
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

Aguarda finalizar — vai aparecer `Created version '1' of model 'quantsignal-ranker'`.

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

```
quantsignal/
├── app/
│   ├── main.py              # entrypoint FastAPI
│   ├── schemas.py           # modelos Pydantic
│   └── routers/
│       ├── signals.py       # GET /signals
│       ├── explain.py       # GET /explain/{ticker}
│       └── model_info.py    # GET /model/info
├── pipeline/
│   ├── ingest.py            # busca dados do Yahoo Finance
│   ├── features.py          # cálculo de fatores quantitativos
│   ├── train.py             # treinamento + MLFlow tracking
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
    ├── wrapper.py
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

Para destruir toda a infraestrutura:
```bash
terraform destroy
```

---

## CI/CD

Todo push na branch `master` dispara automaticamente:

1. **CI** — lint com Ruff + testes com pytest
2. **CD** — build da imagem Docker → push pro ECR → deploy no EKS

O retreinamento acontece automaticamente toda segunda-feira às 6h UTC.

---

## Autor

Diogo Moraes — [LinkedIn](https://linkedin.com/in/diogopelinsonmoraes) · [GitHub](https://github.com/diogopelinson)