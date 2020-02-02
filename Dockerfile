FROM alpine:latest

LABEL MAINTAINER=tanzaku

RUN apk add --update \
    udev \
    ttf-freefont \
    chromium \
    chromium-chromedriver \
    python3

RUN pip3 install --upgrade pip && \
    # pip install "chromedriver-binary<$(chrome --version | awk '{ print $NF }' )" && \
    pip install selenium

ADD src/main.py /app/bin/main.py

ENTRYPOINT ["python3", "/app/bin/main.py"]
