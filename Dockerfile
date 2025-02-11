FROM alpine:latest
RUN mkdir /app
COPY . /app
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories && apk update && apk add python3 py3-pip tzdata && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && cd /app && pip install --no-cache-dir -r ./requirements.txt --break-system-packages && apk -v cache clean
WORKDIR /app
CMD celery -A task worker --loglevel=info