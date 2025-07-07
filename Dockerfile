FROM python:3.11-slim-buster

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install uv --upgrade && && \
    uv pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


