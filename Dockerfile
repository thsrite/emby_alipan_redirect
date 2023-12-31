FROM python:3.9-slim
ENV LANG="C.UTF-8" \
    HOME="/alipan_redirect" \
    TZ="Asia/Shanghai" \
    PUID=0 \
    PGID=0 \
    UMASK=000
WORKDIR ./alipan_redirect
ADD . .
RUN apt-get update \
    && apt-get -y install \
        gosu \
        bash \
        dumb-init \
   && cp -f /alipan_redirect/entrypoint /entrypoint \
   && chmod +x /entrypoint \
   && groupadd -r redirect -g 911 \
   && useradd -r redirect -g redirect -d /alipan_redirect -s /bin/bash -u 911 \
   && pip install -r requirements.txt

ENTRYPOINT [ "/entrypoint" ]