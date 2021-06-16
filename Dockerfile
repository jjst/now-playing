FROM jjst/alpine-python-grpcio:3.13-python3.9-grpcio-1.38.0

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app


COPY requirements.txt /usr/src/app/

RUN apk add git && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del git

COPY . /usr/src/app

EXPOSE 8080

ENTRYPOINT ["gunicorn"]

CMD ["--access-logfile=-", "--bind", "0.0.0.0:8080", "--worker-tmp-dir", "/dev/shm", "api:app"]
