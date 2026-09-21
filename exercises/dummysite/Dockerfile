FROM python:3.14-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY controller.py .

USER nobody

CMD ["python3", "controller.py"]
