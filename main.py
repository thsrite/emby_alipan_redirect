import multiprocessing

import uvicorn
from fastapi import FastAPI
from uvicorn import Config

import aliyunpan
import filechange
from api.apiv1 import api_router

if __name__ == '__main__':
    # 阿里云盘
    alipan = aliyunpan.AliyunPan()
    # 文件监控
    filechange.FileChange().start()

    # App
    App = FastAPI(title='aliyunpan_strm',
                  openapi_url="/api/v1/openapi.json")

    # API路由
    App.include_router(api_router, prefix="/api")

    # uvicorn服务
    Server = uvicorn.Server(Config(App, host='0.0.0.0', port=55655,
                                   reload=False, workers=multiprocessing.cpu_count()))

    # 启动服务
    Server.run()
