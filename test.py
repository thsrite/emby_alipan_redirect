import os
import shutil
import urllib.parse
from pathlib import Path


def create_strm_file(dest_dir, destination, emby_directory):
    # 获取视频文件名和目录
    video_name = Path(dest_dir).name

    dest_path = Path(dest_dir).parent

    # 构造.strm文件路径
    strm_path = os.path.join(dest_path, f"{os.path.splitext(video_name)[0]}.strm")

    # 本地挂载路径转为emby路径
    dest_dir = dest_dir.replace(destination, emby_directory)

    # 写入.strm文件
    with open(strm_path, 'w') as f:
        f.write(dest_dir)


def copy_files(source, destination, emby_directory):
    if not os.path.exists(destination):
        os.makedirs(destination)

    video_formats = ('.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.iso', '.mpg')

    for root, dirs, files in os.walk(source):
        # 如果遇到名为'extrafanart'的文件夹，则跳过处理该文件夹，继续处理其他文件夹
        if 'extrafanart' in dirs:
            dirs.remove('extrafanart')

        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(destination, os.path.relpath(source_file, source))
            dest_dir = os.path.dirname(dest_file)

            # 创建目标目录中缺少的文件夹
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            # 如果目标文件已存在，跳过处理
            if os.path.exists(dest_file):
                continue

            # 如果遇到名为'trailers'的文件夹
            if os.path.basename(root) == 'trailers':
                backdrops_dir = os.path.join(os.path.dirname(dest_dir), 'backdrops')
                if not os.path.exists(backdrops_dir):
                    os.makedirs(backdrops_dir)
                create_strm_file(backdrops_dir, destination, emby_directory)

                trailers_dir = os.path.join(os.path.dirname(dest_dir), 'trailers')
                if not os.path.exists(trailers_dir):
                    os.makedirs(trailers_dir)
                create_strm_file(trailers_dir, destination, emby_directory)
            else:
                # 如果视频文件小于1MB，则直接复制，不创建.strm文件
                if os.path.getsize(source_file) < 1024 * 1024:
                    shutil.copy2(source_file, dest_file)
                    continue

                if file.lower().endswith(video_formats):
                    # 创建.strm文件
                    create_strm_file(dest_dir, destination, emby_directory)
                else:
                    # 复制文件
                    shutil.copy2(source_file, dest_file)


# 指定目录a和目录b的路径
source_directory = '/mnt/user/downloads/CloudDrive/aliyun/emby'
destination_directory = '/mnt/user/downloads/link/aliyun'
emby_directory = '/data/aliyun'

copy_files(source_directory, destination_directory, emby_directory)
