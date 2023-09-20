from fastapi import APIRouter

import aliyunpan

router = APIRouter()


@router.post("/", summary="根据路径获取播放链接")
def get_download_url(path: dict):
    """
    根据路径获取播放链接
    """
    print(path)
    alipan = aliyunpan.AliyunPan()
    return {'code': 0, 'data': alipan.get_download_url(path.get("dest_dir"))}
