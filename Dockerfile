FROM jjst/alpine-python-grpcio:3.13-python3.9-grpcio-1.38.0

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app


COPY requirements.txt /usr/src/app/

RUN apk add git && \
    pip3 install --no-cache-dir -r requirements/prod.txt

COPY . /usr/src/app

WORKDIR /usr/src/app/
EXPOSE 8080
# Support dynamically loading config from git
ENV GIT_CONFIG_REPOSITORY="https://github.com/jjst/now-playing.git"
ENV GIT_CONFIG_REPOSITORY_SUBFOLDER="conf"
ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["-m", "api"]
