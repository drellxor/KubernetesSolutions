FROM python:3.14-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV SERVER_PORT=8000
EXPOSE 8000

USER nobody

CMD ["python3", "app.py"]
