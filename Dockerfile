FROM python:3.12-slim AS builder
WORKDIR /src

# Copy and build all wheels into /wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir -r requirements.txt --wheel-dir=/wheels

FROM python:3.12-slim
WORKDIR /app

# Copy the wheels and install them via requirements.txt
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-index --find-links=/wheels -r requirements.txt

# Copy your application code
COPY . .

CMD ["gunicorn", "-b", "0.0.0:5000", "app:create_app()"]
