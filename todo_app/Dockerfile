FROM python:3.14-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

ENV PORT=8000
ENV IMAGE_FILE=/usr/src/app/files/image.jpg
EXPOSE 8000

# No USER directive: the app caches the image into a mounted volume, which
# Kubernetes creates root-owned. Set securityContext.fsGroup to run non-root.

CMD ["python3", "app.py"]
