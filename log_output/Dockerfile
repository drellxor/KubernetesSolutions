FROM python:3.14-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY writer.py server.py ./

ENV PORT=8000
ENV LOG_FILE=/usr/src/app/files/log.txt
EXPOSE 8000

# No USER directive: the writer needs to create files in the mounted volume,
# which Kubernetes creates root-owned. Set securityContext.fsGroup in the pod
# to run as non-root instead.

CMD ["python3", "server.py"]
