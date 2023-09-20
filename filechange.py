import logging
import os
import shutil
from pathlib import Path
from typing import Any

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

import aliyunpan

logging.basicConfig(filename="alipan_redirect", format='%(asctime)s - %(name)s - %(levelname)s -%(module)s:  %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S ',
                    level=logging.INFO)
logger = logging.getLogger()
KZT = logging.StreamHandler()
KZT.setLevel(logging.DEBUG)
logger.addHandler(KZT)


class FileMonitorHandler(FileSystemEventHandler):
    """
    目录监控响应类
    """

    def __init__(self, monpath: str, sync: Any, **kwargs):
        super(FileMonitorHandler, self).__init__(**kwargs)
        self._watch_path = monpath
        self.sync = sync

    def on_created(self, event):
        self.sync.event_handler(event=event, event_path=event.src_path)

    def on_moved(self, event):
        self.sync.event_handler(event=event, event_path=event.dest_path)


class FileChange:
    def __init__(self):
        self.alipan = aliyunpan.AliyunPan()

        filepath = os.path.join("/mnt", 'config.yaml')
        with open(filepath, 'r') as f:  # 用with读取文件更好
            configs = yaml.load(f, Loader=yaml.FullLoader)  # 按字典格式读取并返回

        self.clouddrive_directory = str(configs["sync"]["clouddrive_directory"])
        self.clouddrive_source_directory = self.clouddrive_directory + str(
            configs["sync"]["clouddrive_source_directory"])
        self.destination_directory = str(configs["sync"]["destination_directory"])
        self.emby_directory = str(configs["sync"]["emby_directory"])

    def start(self):
        # 内部处理系统操作类型选择最优解
        observer = PollingObserver(timeout=10)
        # observer = Observer(timeout=10)
        observer.schedule(FileMonitorHandler(self.clouddrive_source_directory, self),
                          path=self.clouddrive_source_directory, recursive=True)
        logger.info(f"开始监控文件夹 {self.clouddrive_source_directory}")
        observer.daemon = True
        observer.start()

    def event_handler(self, event, event_path: str):
        # 文件夹同步创建
        if event.is_directory:
            target_path = event_path.replace(self.clouddrive_source_directory, self.destination_directory)
            # 目标文件夹不存在则创建
            if not Path(target_path).exists():
                logger.info(f"创建目标文件夹 {target_path}")
                os.makedirs(target_path)
        else:
            # 文件：nfo、图片、视频文件
            dest_file = event_path.replace(self.clouddrive_source_directory, self.destination_directory)

            # 目标文件夹不存在则创建
            if not Path(dest_file).parent.exists():
                logger.info(f"创建目标文件夹 {Path(dest_file).parent}")
                os.makedirs(Path(dest_file).parent)

            # 视频文件创建.strm文件
            video_formats = ('.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.iso', '.mpg')
            if event_path.lower().endswith(video_formats):
                # 如果视频文件小于1MB，则直接复制，不创建.strm文件
                if os.path.getsize(event_path) < 1024 * 1024:
                    shutil.copy2(event_path, dest_file)
                    logger.info(f"复制视频文件 {event_path} 到 {dest_file}")
                    # 本地挂载路径转为emby路径
                    dest_dir = dest_file.replace(self.destination_directory, self.emby_directory)
                    # 获取阿里云盘file_id，存储
                    self.alipan.save_new_file_id(dest_dir=dest_dir)
                else:
                    # 创建.strm文件
                    self.create_strm_file(dest_file)
            else:
                # 其他nfo、jpg等复制文件
                shutil.copy2(event_path, dest_file)
                logger.info(f"复制其他文件 {event_path} 到 {dest_file}")

    def create_strm_file(self, dest_dir):
        # 获取视频文件名和目录
        video_name = Path(dest_dir).name

        dest_path = Path(dest_dir).parent

        if not dest_path.exists():
            logger.info(f"创建目标文件夹 {dest_path}")
            os.makedirs(str(dest_path))

        # 构造.strm文件路径
        strm_path = os.path.join(dest_path, f"{os.path.splitext(video_name)[0]}.strm")

        # 本地挂载路径转为emby路径
        dest_dir = dest_dir.replace(self.destination_directory, self.emby_directory)

        # 写入.strm文件
        with open(strm_path, 'w') as f:
            f.write(dest_dir)

        logger.info(f"创建strm文件 {strm_path}")

        # 获取阿里云盘file_id，存储
        self.alipan.save_new_file_id(dest_dir=dest_dir)
