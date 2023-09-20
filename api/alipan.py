from fastapi import APIRouter

import aliyunpan

router = APIRouter()


@router.get("/", summary="根据路径获取播放链接")
def get_download_url(dest_dir: str):
    """
    根据路径获取播放链接
    """
    alipan = aliyunpan.AliyunPan()
    return {'code': 0, 'data': alipan.get_download_url(dest_dir)}
