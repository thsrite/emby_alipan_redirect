实现效果：

1.监控cd2挂载本地后的路径，如果新文件创建自动生成strm文件

2.emby播放时请求alipan_redirect api，获取阿里云盘直链，获取不到则返回cd2下载链接播放（实测nginx 重定向阿里云盘直链不走服务端）

3.emby可正常播放本地资源

问题点！！！不能硬解了，不能硬解了，不能硬解了。我尝试本地资源可硬解，网盘资源不可硬解，未成功。

注：首次初始化可手动执行test.py

```
config.yaml配置如下

sync:
  # 阿里云盘里存放媒体资源的根路径
  alipan_directory_name: "emby"
  # cd2挂载本地的根路径
  clouddrive_directory: "/mnt/user/downloads/CloudDrive"
  # cd2挂载本地的网盘路径+阿里云盘资源路径
  clouddrive_source_directory: "/aliyun/emby"
  # 本地生成strm的路径
  destination_directory: "/mnt/user/downloads/link/aliyun"
  # emby挂载本地生成strm的路径
  emby_directory: "/data/aliyun"
  # cd2
  clouddrive_url: "192.168.31.103:19798"
  # 是否获取阿里云盘直链，否则返回cd2连接
  straight_chain: true
```

```
docker run -d --name alipan_redirect \
 -p 55655:55655 \
 -v /mnt/user/appdata/alipan_redirect/config.yaml:/mnt/config.yaml \
 -v /mnt/user/downloads:/mnt/user/downloads \
 -v /mnt/user/appdata/alipan_redirect/folder_files.json:/mnt/folder_files.json \
 -v /mnt/user/appdata/alipan_notify/aligo.json:/root/.aligo/aligo.json \
thsrite/alipan-redirect:latest
```
需要搭配nginx使用  nginx.conf、conf.d见github

```
docker run -d --name nginx -p 8088:80 -p 4454:443 \
 -v /mnt/user/appdata/nginx/conf.d/:/etc/nginx/conf.d \
 -v /mnt/user/appdata/nginx/embyCache/:/var/cache/nginx/emby \
 -v /mnt/user/appdata/nginx/nginx.conf:/etc/nginx/nginx.conf \
nginx:alpine
```

