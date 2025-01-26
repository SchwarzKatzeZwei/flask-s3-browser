FROM python:3.11-slim as builder
ADD ./requirements.txt /tmp
RUN apt-get update && apt-get install -y \
    zip \
    convmv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /tmp/requirements.txt

FROM python:3.11-slim as runner

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/bin /usr/bin

WORKDIR /app
