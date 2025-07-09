# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["python", "src/train.py", "--help"]
