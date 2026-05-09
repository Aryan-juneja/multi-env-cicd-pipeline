# Multi-Environment CI/CD Pipeline

A production-style CI/CD pipeline that builds, tests, scans, and publishes a Docker image, then deploys it to Kubernetes across **dev**, **staging**, and **prod** environments via Helm — with manual approval between staging and prod.

## Architecture

```
GitHub push -> GitHub Actions
                |- pytest
                |- docker build
                |- Trivy image scan
                |- push to AWS ECR (tag = git SHA)
                v
        Helm upgrade --install
                |
   +------------+------------+------------+
   |            |            |            |
  dev       staging      [approval]     prod
 (auto)      (on tag)    (manual)       (manual)
```

- **Local dev cluster**: `kind`
- **Remote cluster**: single-node `k3s` on an AWS EC2 t2.micro (free tier), with three namespaces (`dev`, `staging`, `prod`)
- **Image registry**: AWS ECR
- **Deployment**: Helm chart with per-environment values files
- **Security**: Trivy image scanning in CI

## Stack

| Layer        | Tool                                  |
|--------------|---------------------------------------|
| App          | Python 3.9, FastAPI                   |
| Container    | Docker (multi-stage, non-root)        |
| Registry     | AWS ECR                               |
| Orchestrator | Kubernetes (kind locally, k3s on EC2) |
| Packaging    | Helm                                  |
| CI/CD        | GitHub Actions                        |
| Security     | Trivy                                 |

## Roadmap

- [x] Phase 1 — FastAPI app with `/`, `/health`, `/version` + tests
- [x] Phase 2 — Multi-stage Dockerfile, non-root user (UID 10001), `.dockerignore`
- [x] Phase 3 — Raw Kubernetes manifests + local `kind` cluster + ingress-nginx
- [x] Phase 4 — Helm chart with `values-{dev,staging,prod}.yaml`, three releases on one cluster
- [ ] Phase 5 — GitHub Actions CI: test, build, Trivy scan, push to ECR
- [ ] Phase 6 — GitHub Actions CD: deploy to dev/staging/prod with approval gate
- [ ] Phase 6.5 — k3s on EC2 t2.micro (3 namespaces for dev/staging/prod)
- [ ] Phase 7 — Polish: architecture diagram, screenshots, release tagging

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Run tests
pytest -v

# Run the app
uvicorn app.main:app --reload --port 8000

# Try it
curl http://localhost:8000/health
curl http://localhost:8000/version
```

## Run in Docker

```bash
docker build \
  --build-arg APP_VERSION=0.1.0 \
  --build-arg GIT_SHA=$(git rev-parse --short HEAD) \
  -t multi-env-cicd-pipeline:dev .

docker run --rm -p 8000:8000 multi-env-cicd-pipeline:dev
```

## Deploy locally on `kind` (3 envs on 1 cluster)

```bash
# Create cluster (host 8080 -> ingress 80, host 8443 -> ingress 443)
kind create cluster --name multi-env-cicd --config infra/kind-config.yaml

# Install ingress-nginx
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx --for=condition=available --timeout=180s deployment/ingress-nginx-controller

# Load local image into the cluster
kind load docker-image multi-env-cicd-pipeline:dev --name multi-env-cicd

# Install all three environments
for env in dev staging prod; do
  helm upgrade --install myapp ./chart \
    -f chart/values-$env.yaml \
    -n $env --create-namespace \
    --wait
done

# Hit each environment through its own ingress host
curl -H "Host: dev.myapp.local"     http://localhost:8080/version
curl -H "Host: staging.myapp.local" http://localhost:8080/version
curl -H "Host: prod.myapp.local"    http://localhost:8080/version

# Inspect a release
helm list -A
helm get values myapp -n prod
helm history myapp -n prod

# Tear down
helm uninstall myapp -n dev
helm uninstall myapp -n staging
helm uninstall myapp -n prod
kind delete cluster --name multi-env-cicd
```

## Project layout

```
multi-env-cicd-pipeline/
├── app/                  # FastAPI app
│   └── main.py
├── tests/                # Unit tests
├── requirements.txt      # Runtime deps
├── requirements-dev.txt  # Test/dev deps
├── Dockerfile            # (Phase 2)
├── chart/                # Helm chart
│   ├── Chart.yaml
│   ├── values.yaml          # defaults
│   ├── values-dev.yaml      # per-env overrides
│   ├── values-staging.yaml
│   ├── values-prod.yaml
│   └── templates/
├── .github/workflows/    # CI/CD pipelines (Phase 5+)
└── infra/                # kind config + k3s bootstrap (Phase 6.5)
```
