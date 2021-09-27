FROM python:3.9

ADD ./requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
# CMD [ "flask", "run" ]
