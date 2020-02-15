FROM lambci/lambda:build-python3.6

ENV AWS_DEFAULT_REGION us-east-1
ENV PYTHON_VER  3.6
ENV APP_DIR /var/task
ENV ZIP_DIR ${APP_DIR}/data
ENV PYTHON_LIB_DIR ${ZIP_DIR}/python/lib/python${PYTHON_VER}/site-packages
ENV OUTPUT_DIR ${APP_DIR}/target

CMD mkdir -p ${PYTHON_LIB_DIR} ${OUTPUT_DIR} && \
    cd ${APP_DIR} && \
    unzip -o ${APP_DIR}/tmp/headless-chromium.zip -d ${ZIP_DIR}/bin && \
    unzip -o ${APP_DIR}/tmp/chromedriver.zip -d ${ZIP_DIR}/bin && \
    pip install -r requirements.txt -t ${PYTHON_LIB_DIR} && \
    rm ${OUTPUT_DIR}/*.zip && \
    pushd ${ZIP_DIR} && \
    zip -r9 ${OUTPUT_DIR}/deploy_layer.zip . && \
    popd && \
    rm -rf ${ZIP_DIR}
