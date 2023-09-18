FROM python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements-base.txt

COPY src/ src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
