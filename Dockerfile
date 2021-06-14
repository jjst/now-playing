FROM jjst/alpine-python-grpcio:3.13-python3.9-grpcio-1.38.0

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

# Required to build grpcio
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

EXPOSE 8080

ENTRYPOINT ["gunicorn"]

CMD ["--access-logfile=-", "--bind", "0.0.0.0:8080", "api:app"]
