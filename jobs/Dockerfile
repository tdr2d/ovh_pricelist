FROM python:3.10.12-alpine3.18
WORKDIR /job
COPY *.py .
COPY *.txt .
RUN apk update && \
    apk add make automake gcc g++ subversion python3-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt