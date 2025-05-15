FROM python:3.12-slim AS builder
WORKDIR /src
COPY requirements.txt .
RUN pip wheel -r requirements.txt --wheel-dir /wheels

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels *
COPY . .
CMD ["gunicorn","-b","0.0.0:5000","app:create_app()"]
