FROM python:3.14-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY app.py .

USER nobody

CMD ["python3", "app.py"]
