//author: @bpking  https://github.com/bpking1/embyExternalUrl
//查看日志: "docker logs -f -n 10 emby-nginx 2>&1  | grep js:"
import config from "./constant.js";
import util from "./util.js";

async function redirect2Pan(r) {
  const alipanDirectGetApiPath = config.alipanDirectGetApiPath;
  const embyMountPath = config.embyMountPath;
  //fetch mount emby/jellyfin file path
  const itemInfo = util.getItemInfo(r);
  r.warn(`itemInfoUri: ${itemInfo.itemInfoUri}`);
  const embyRes = await fetchEmbyFilePath(itemInfo.itemInfoUri, itemInfo.Etag);
  if (embyRes.startsWith("error")) {
    r.error(embyRes);
    r.return(500, embyRes);
    return;
  }
  r.warn(`mount emby file path: ${embyRes}`);
  
  if (!embyRes.startsWith(embyMountPath)){
    let url = util.getCurrentRequestUrl(r);
    r.warn(`getCurrentRequestUrl: ${url}`);
    r.return(302, url);
    return;
  } 

  //fetch cd2 | alipan direct link
   let alipantRes = await fetchAlipanDirectPathApi(
     alipanDirectGetApiPath,
     embyRes
   );
   if (!alipantRes.startsWith("error")) {
     r.warn(`redirect to: ${alipantRes}`);
     r.return(302, alipantRes);
     return;
   }

  r.error(alipantRes);
  r.return(500, alipantRes);
  return;
}


// 拦截 PlaybackInfo 请求，防止客户端转码（转容器）
async function transferPlaybackInfo(r) {
  const embyMountPath = config.embyMountPath;
  // 1 获取 itemId
  const itemInfo = util.getItemInfo(r);
  
  // 判断是不是网盘资源
  const embyRes = await fetchEmbyFilePath(itemInfo.itemInfoUri, itemInfo.Etag);
  if (embyRes.startsWith("error")) {
    r.error(embyRes);
    r.return(500, embyRes);
    return;
  }
  r.warn(`mount emby file path: ${embyRes}`);
  
  if (!embyRes.startsWith(embyMountPath)){
    return r.return(302, util.getCurrentRequestUrl(r));
  } 

  // 2 手动请求 PlaybackInfo
  const response = await ngx.fetch(itemInfo.itemInfoUri, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });
  // 3 返回
  if (response.ok) {
    const body = await response.json();
    r.headersOut["Content-Type"] = "application/json;charset=utf-8";
    return r.return(200, JSON.stringify(body));
  }
  return r.return(302, util.getCurrentRequestUrl(r));
}

async function fetchAlipanDirectPathApi(apiPath, filePath) {
  const alistRequestBody = {
    dest_dir: filePath,
  };
  try {
    const response = await ngx.fetch(apiPath, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      max_response_body_size: 65535,
      body: JSON.stringify(alistRequestBody),
    });
    if (response.ok) {
      const result = await response.json();
      if (result === null || result === undefined) {
        return `error: alipan_direct_path_api response is null`;
      }
      if (result.code == "0") {
        if (result.data) {
          return result.data;
        }
        return `error: alipan_direct_path_api ${result.code} ${result.data}`;
      }
     
      return `error: alipan_direct_path_api ${result.code} ${result.data}`;
    } else {
      return `error: alipan_direct_path_api ${response.status} ${response.statusText}`;
    }
  } catch (error) {
    return `error: alipan_direct_path_api ${error}`;
  }
}

async function fetchEmbyFilePath(itemInfoUri, Etag) {
  try {
    const res = await ngx.fetch(itemInfoUri, {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=utf-8",
        "Content-Length": 0,
      },
      max_response_body_size: 65535,
    });
    if (res.ok) {
      const result = await res.json();
      if (result === null || result === undefined) {
        return `error: emby_api itemInfoUri response is null`;
      }
      if (Etag) {
        const mediaSource = result.MediaSources.find((m) => m.ETag == Etag);
        if (mediaSource && mediaSource.Path) {
          return mediaSource.Path;
        }
      }
      return result.MediaSources[0].Path;
    } else {
      return `error: emby_api ${res.status} ${res.statusText}`;
    }
  } catch (error) {
    return `error: emby_api fetch mediaItemInfo failed,  ${error}`;
  }
}

export default { redirect2Pan, fetchEmbyFilePath, transferPlaybackInfo };
