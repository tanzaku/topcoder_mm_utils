FROM lambci/lambda:build-python3.6

ENV AWS_DEFAULT_REGION us-east-1
ENV PYTHON_VER  3.6
ENV APP_DIR /var/task
ENV ZIP_DIR ${APP_DIR}/data
ENV PYTHON_LIB_DIR ${ZIP_DIR}/python/lib/python${PYTHON_VER}/site-packages
ENV OUTPUT_DIR ${APP_DIR}/target

RUN cd /tmp && \
    yum install -y wget && \
    wget https://ftp.postgresql.org/pub/source/v9.4.7/postgresql-9.4.7.tar.gz && \
    tar zxfv postgresql-9.4.7.tar.gz && \
    cd postgresql-9.4.7 && \
    PG_DIR=/tmp/pg && \
    ./configure --prefix $PG_DIR --without-readline --without-zlib && \
    make && \
    make install && \
    cd - && \
    wget http://initd.org/psycopg/tarballs/PSYCOPG-2-6/psycopg2-2.6.1.tar.gz && \
    tar zxfv psycopg2-2.6.1.tar.gz && \
    cd psycopg2-2.6.1 && \
    sed -i.bak -e 's!^#pg_config=.*$!pg_config=/tmp/pg/bin/pg_config!g' -e 's/^#static_libpq=.*$/static_libpq=1/g' setup.cfg && \
    LD_LIBRARY_PATH=$PG_DIR/lib:$LD_LIBRARY_PATH python setup.py build && \
    cp -r build/lib.linux-x86_64-3.6/psycopg2 ~

CMD mkdir -p ${PYTHON_LIB_DIR} ${OUTPUT_DIR} && \
    cp -r ~/psycopg2 ${PYTHON_LIB_DIR}/ && \
    cd ${APP_DIR} && \
    unzip -o ${APP_DIR}/tmp/headless-chromium.zip -d ${ZIP_DIR}/bin && \
    unzip -o ${APP_DIR}/tmp/chromedriver.zip -d ${ZIP_DIR}/bin && \
    pip install -r requirements.txt -t ${PYTHON_LIB_DIR} && \
    rm ${OUTPUT_DIR}/*.zip && \
    pushd ${ZIP_DIR} && \
    zip -r9 ${OUTPUT_DIR}/deploy_layer.zip . && \
    popd && \
    rm -rf ${ZIP_DIR}
