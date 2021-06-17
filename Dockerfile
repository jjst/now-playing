FROM jjst/alpine-python-grpcio:3.13-python3.9-grpcio-1.38.0

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app


COPY requirements.txt /usr/src/app/

RUN apk add git && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

WORKDIR /usr/src/app/src
EXPOSE 8080
ENTRYPOINT ["gunicorn"]
# Support dynamically loading config from git
ENV LOADERS_FOR_DYNACONF="['git_config_loader', 'dynaconf.loaders.env_loader']"
ENV GIT_REPO_FOR_DYNACONF="https://github.com/jjst/now-playing.git"
ENV GIT_REPO_SUBFOLDER_FOR_DYNACONF="conf"
CMD ["--access-logfile=-", "--bind", "0.0.0.0:8080", "--worker-tmp-dir", "/dev/shm", "api:app"]
