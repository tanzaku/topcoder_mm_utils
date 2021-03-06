FROM alpine:latest

LABEL MAINTAINER=tanzaku

RUN apk add --update \
    udev \
    ttf-freefont \
    chromium \
    chromium-chromedriver \
    python3 \
    postgresql-dev \
    gcc libc-dev \
    python3-dev

RUN pip3 install --upgrade pip && \
    # pip install "chromedriver-binary<$(chrome --version | awk '{ print $NF }' )" && \
    pip install selenium && \
    pip install psycopg2

ADD src/main.py /app/bin/main.py
ADD src/scrape.py /app/bin/scrape.py

# CMD ["python3", "/app/bin/main.py"]
CMD ["python3", "/app/bin/scrape.py"]
