FROM redis:6.2.4-alpine

RUN apk add python3 py3-pip && pip3 install redis

EXPOSE 8001

COPY healthcheck.py .
COPY entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]
