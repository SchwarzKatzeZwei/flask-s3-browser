FROM python:3.9

ADD ./requirements.txt /tmp
RUN apt-get update && apt-get install -y \
    zip \
    convmv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
# CMD [ "flask", "run" ]
