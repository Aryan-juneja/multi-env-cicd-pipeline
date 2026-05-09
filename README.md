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
- [ ] Phase 2 — Multi-stage Dockerfile, non-root user
- [ ] Phase 3 — Raw Kubernetes manifests (deploy locally on kind)
- [ ] Phase 4 — Helm chart with `values-{dev,staging,prod}.yaml`
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

## Project layout

```
multi-env-cicd-pipeline/
├── app/                  # FastAPI app
│   └── main.py
├── tests/                # Unit tests
├── requirements.txt      # Runtime deps
├── requirements-dev.txt  # Test/dev deps
├── Dockerfile            # (Phase 2)
├── chart/                # Helm chart (Phase 4)
├── .github/workflows/    # CI/CD pipelines (Phase 5+)
└── infra/                # k3s bootstrap script (Phase 6.5)
```
