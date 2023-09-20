// export constant allocation
// 根据实际情况修改下面的设置

// 这里默认emby/jellyfin的地址是宿主机,要注意iptables给容器放行端口
const embyHost = "http://192.168.31.103:8096";
// emby外网访问地址
const embyHostNet = "https://emby.abc.com";

// rclone 的挂载目录, 例如将od, gd挂载到/mnt目录下:  /mnt/onedrive  /mnt/gd ,那么这里 就填写 /mnt
const embyMountPath = "/data/aliyun";

// emby/jellyfin api key, 在emby/jellyfin后台设置
const embyApiKey = "32432432423423432423423";

// alipan_redirect api路径
const alipanDirectGetApiPath = "http://192.168.31.103:55655/api/alipan/"

export default {
  embyHost,
  embyHostNet,
  embyMountPath,
  embyApiKey,
  alipanDirectGetApiPath
}
