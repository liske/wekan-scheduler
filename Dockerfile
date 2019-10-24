FROM alpine:3.10

COPY requirements.txt src/ /app/wekan-scheduler/

WORKDIR /app/wekan-scheduler

RUN apk add --no-cache ca-certificates git python3 && \
    pip3 install -r requirements.txt && \
    apk del git

ENV PYTHONUNBUFFERED true
CMD ["./scheduler.py" ]
