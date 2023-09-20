import config from "./constant.js";

function generateUrl(r, host, uri) {
  let url = host + uri;
  let isFirst = true;
  for (const key in r.args) {
    url += isFirst ? "?" : "&";
    url += `${key}=${r.args[key]}`;
    isFirst = false;
  }
  return url;
}

function getEmbyOriginRequestUrl(r) {
  const embyHost = config.embyHost;
  return generateUrl(r, embyHost, r.uri);
}

function getCurrentRequestUrl(r) {
  const embyHostNet = config.embyHostNet;
  const embyHost = config.embyHost;
  const host = r.headersIn["Host"];
  if (host.startsWith(192) || host.startsWith(172) || host.startsWith(10) ) {
       return generateUrl(r, embyHost, r.uri);
  } else {
       let url = generateUrl(r, embyHostNet, r.uri);
       return url;
  }
}

function getItemInfo(r) {
  const embyHost = config.embyHost;
  const embyApiKey = config.embyApiKey;
  const regex = /[A-Za-z0-9]+/g;
  const itemId = r.uri.replace("emby", "").replace(/-/g, "").match(regex)[1];
  const mediaSourceId = r.args.MediaSourceId
    ? r.args.MediaSourceId
    : r.args.mediaSourceId;
  const Etag = r.args.Tag;
  let api_key = r.args["X-Emby-Token"]
    ? r.args["X-Emby-Token"]
    : r.args.api_key;
  api_key = api_key ? api_key : embyApiKey;
  let itemInfoUri = "";
  if (mediaSourceId) {
    itemInfoUri = `${embyHost}/Items/${itemId}/PlaybackInfo?MediaSourceId=${mediaSourceId}&api_key=${api_key}`;
  } else {
    itemInfoUri = `${embyHost}/Items/${itemId}/PlaybackInfo?api_key=${api_key}`;
  }
  return { itemId, mediaSourceId, Etag, api_key, itemInfoUri };
}

export default { getItemInfo, getCurrentRequestUrl, getEmbyOriginRequestUrl };
