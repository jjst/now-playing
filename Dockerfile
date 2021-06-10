FROM python:3.9-alpine3.13

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

# Required to build grpcio
RUN apk add g++

RUN pip3 install --no-cache-dir -r requirements.txt

RUN apk del g++

COPY . /usr/src/app

EXPOSE 8080

ENTRYPOINT ["waitress-serve"]

CMD ["api:app"]
