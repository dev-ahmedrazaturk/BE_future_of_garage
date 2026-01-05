FROM python:3.9-slim


WORKDIR /app
COPY . .

RUN python -m venv /venv
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

CMD ["/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0"]
