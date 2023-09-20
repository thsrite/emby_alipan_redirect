FROM python:3.9-slim
ENV TZ=Asia/Shanghai
WORKDIR ./alipan_redirect
ADD . .
RUN pip install -r requirements.txt
CMD ["python", "./main.py"]