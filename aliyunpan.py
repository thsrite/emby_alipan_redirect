import json
import logging
import os
import urllib.parse
from pathlib import Path

import yaml
from aligo import Aligo

from singleton import Singleton

logger = logging.getLogger()


class AliyunPan(metaclass=Singleton):
    def __init__(self):
        filepath = os.path.join("/mnt", 'config.yaml')
        with open(filepath, 'r') as f:  # 用with读取文件更好
            configs = yaml.load(f, Loader=yaml.FullLoader)  # 按字典格式读取并返回

        self.REFRESH_TOKEN = None
        self.alipan_directory_name = str(configs["sync"]["alipan_directory_name"])
        self.emby_directory = str(configs["sync"]["emby_directory"])
        self.clouddrive_source_directory = str(configs["sync"]["clouddrive_source_directory"])
        self.clouddrive_url = str(configs["sync"]["clouddrive_url"])
        self.straight_chain = bool(configs["sync"]["straight_chain"])

        self.RMT_MEDIA = ['.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.iso', '.mpg']
        # 第一次使用，会弹出二维码，供扫描登录
        self._ali = Aligo(level=logging.INFO, refresh_token=self.REFRESH_TOKEN)

        # 本次文件存储路径
        self.__folder_json = '/mnt/folder_files.json'
        # 文件夹->文件映射关系
        self.__folder_files = {}
        # 读取已有本地文件
        if Path(self.__folder_json).exists():
            with open(self.__folder_json, 'r') as file:
                content = file.read()
                if content:
                    self.__folder_files = json.loads(content)
        else:
            self.sync_aliyunpan()

    def __get_folder_files(self, parent, file):
        '''
        获取文件夹下级文件存储
        :param parent:
        :param file:
        :return:
        '''
        parent_file_id = None
        if file and file.type == 'folder':
            parent_file_id = file.file_id
        if file and file.type == 'file' and Path(file.name).suffix in self.RMT_MEDIA:
            path = Path(parent).joinpath(file.name)
            path = str(path).replace(self.alipan_directory_name, self.emby_directory)
            path = path.replace("\\", "/")
            self.__folder_files[path] = file.file_id

        files = self._ali.get_file_list(parent_file_id=parent_file_id)
        if files:
            for file2 in files:
                path = Path(parent).joinpath(file2.name)
                path = str(path).replace(self.alipan_directory_name, self.emby_directory)
                path = path.replace("\\", "/")
                if file2.type == 'folder':
                    self.__get_folder_files(path, file2)
                elif Path(file2.name).suffix in self.RMT_MEDIA:
                    self.__folder_files[path] = file2.file_id

    def sync_aliyunpan(self):
        '''
        同步阿里云文件
        '''
        logger.info("同步阿里云文件")

        # 获取用户信息
        user = self._ali.get_user()
        logger.info(user)

        # 读取已有本地文件
        if Path(self.__folder_json).exists():
            with open(self.__folder_json, 'r') as file:
                content = file.read()
                if content:
                    self.__folder_files = json.loads(content)

        # 获取网盘根目录文件列表
        ll = self._ali.get_file_list()
        # 遍历文件列表
        for file in ll:
            if file.name == self.alipan_directory_name:
                self.__get_folder_files(self.alipan_directory_name, file)

        # 最终写入文件
        if self.__folder_files:
            logger.info(f"开始写入本地文件 {self.__folder_json}")
            file = open(self.__folder_json, 'w')
            file.write(json.dumps(self.__folder_files))
            file.close()
        else:
            logger.warning(f"未获取到文件列表")

    def save_new_file_id(self, dest_dir):
        """
        存储新创建文件的file_id
        :param dest_dir:
        :return:
        """
        alipan_dir = str(dest_dir).replace(self.emby_directory, self.alipan_directory_name)
        file = self._ali.get_file_by_path(path=alipan_dir)
        if file:
            logger.info(f"获取到 {alipan_dir} 阿里云盘file_id {file.file_id}")
            self.__folder_files[dest_dir] = file.file_id
            logger.info(f"开始写入本地文件 {self.__folder_json}")
            file = open(self.__folder_json, 'w')
            file.write(json.dumps(self.__folder_files))
            file.close()

    def get_download_url(self, dest_dir: str):
        """
        获取阿里云盘播放直链（有效期4个小时)
        :param dest_dir:
        :return:
        """
        # 替换路径中的\为/
        dest_dir = dest_dir.replace("\\", "/")
        file_id = self.__folder_files.get(dest_dir)
        if not self.straight_chain or not file_id:
            # 未查询到阿里云盘file_id 返回cd2连接

            dest_dir = dest_dir.replace(self.emby_directory, "")
            # 对盘符之后的所有内容进行url转码
            dest_dir = self.clouddrive_source_directory + dest_dir
            dest_dir = urllib.parse.quote(str(dest_dir), safe='')
            dest_dir = f"http://{self.clouddrive_url}/static/http/{self.clouddrive_url}/False/{dest_dir}"
            logger.info(f"获取cd2播放链接 {dest_dir}")
            return dest_dir
        else:
            url = self._ali.get_download_url(file_id=file_id)
            logger.info(f"获取云盘直链 {url}")
            return url.url
