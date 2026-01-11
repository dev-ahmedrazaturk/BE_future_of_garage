# BE_future_of_garage

This repository contains a set of Python FastAPI microservices for the "Future of Garage" project. Services are lightweight, container-ready, and designed to communicate via REST APIs with JWT-based auth. An AWS Lambda is used for sending transactional emails (SES).

**Microservice Architecture**
- **api-gateway**: (entry proxy / routing layer). See [api-gateway/app/main.py](api-gateway/app/main.py#L1-L1).
- **users-auth-api**: authentication and user management; JWT utilities in [users-auth-api/shared/jwt_utils.py](users-auth-api/shared/jwt_utils.py#L1-L1).
- **autostore-api**: core auto-store functionality; invokes an email Lambda via [autostore-api/app/lambda_email.py](autostore-api/app/lambda_email.py#L1-L200). The actual Lambda handler is included at [autostore-api/app/lamdahandler.py](autostore-api/app/lamdahandler.py#L1-L200).
- **service-mot-api**: MOT & services API. Entry point at [service-mot-api/app/main.py](service-mot-api/app/main.py#L1-L200).
- **insurance-api**, **marketplace-api**: (placeholders for business domains).
- **shared/** modules: common JWT utilities duplicated across services; consider consolidating into a single shared package.

**Communication & Auth**
- Transport: HTTP/JSON REST between services.
- Auth: JWT tokens; see the `jwt_utils.py` files under each service's `shared/` directory.

**AWS Lambda (Email) — design & deployment notes**
- Caller: `autostore-api` invokes Lambda using boto3 in [autostore-api/app/lambda_email.py](autostore-api/app/lambda_email.py#L1-L200). Env vars used: `AWS_REGION`, `LAMBDA_NAME`.
- Lambda handler: [autostore-api/app/lamdahandler.py](autostore-api/app/lamdahandler.py#L1-L200) uses AWS SES to send emails; it expects environment variable `FROM_EMAIL`.
- Required IAM permissions for the Lambda (allow SES send):

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": ["ses:SendEmail", "ses:SendRawEmail"],
			"Resource": "*"
		}
	]
}
```

- Deployment options: package the handler as a Lambda (zip) or use AWS SAM / Serverless Framework. Ensure the invoker (service) has AWS SDK credentials (IAM role or keys) that can call `lambda:InvokeFunction` on the Lambda.

**Environment variables (not exhaustive)**
- `AWS_REGION`, `LAMBDA_NAME` — used by `lambda_email.py`.
- `FROM_EMAIL` — used by the Lambda to set the SES Source address.
- DB file paths appear local (sqlite files in service folders). For production, use an RDS or managed DB and configuration via env vars.

**Run locally (examples)**
Run a service with uvicorn (adjust port per service):

```bash
cd users-auth-api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

cd service-mot-api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

Alternatively build each Dockerfile and run containers. Consider adding a `docker-compose.yml` to orchestrate services locally.

**Quick code-review notes & recommended improvements**
- Fix small typos and consistency: `lamdahandler.py` is misspelled (consider `lambda_handler.py`).
- Consolidate `shared/jwt_utils.py` into a single shared package to avoid duplication.
- Add input validation and more robust error handling around the Lambda invocation (`lambda_email.py`) and inside the Lambda handler (e.g., check required keys before sending).
- Add per-service README or `README_SERVICES.md` with service-specific env samples and endpoints.
- Add `docker-compose.yml`, CI (GitHub Actions), linting (flake8/ruff), and tests.

**Where I looked**
- `autostore-api` email invocation: [autostore-api/app/lambda_email.py](autostore-api/app/lambda_email.py#L1-L200)
- `autostore-api` Lambda handler: [autostore-api/app/lamdahandler.py](autostore-api/app/lamdahandler.py#L1-L200)
- `service-mot-api` main endpoints: [service-mot-api/app/main.py](service-mot-api/app/main.py#L1-L200)

---
If you'd like, I can now:
- add a `docker-compose.yml` wiring these services together locally,
- open a PR with the README and additional per-service README files,
- or run static checks / add a GitHub Actions CI workflow.
Tell me which next step you prefer.

"# BE_future_of_garage" 
