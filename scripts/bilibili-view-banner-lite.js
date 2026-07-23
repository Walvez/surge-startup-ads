// 播放页下方 banner 轻量处理（app.bilibili.com / app.biliapi.net ViewUnite）。
// 相对旧版减负：
// 1) 不 hook grpc.* 主机（避免评论卡顿）
// 2) 解压后先 indexOf 扫描协议特征，无广告标记则原样放行
// 3) 不碰评论 / 不碰播放器配置接口
// Banner 会轮换、且不按 UP 绑定；只认投放位协议特征。

const SCAN_MARKERS = [
  "relatedvideo.cm",
  "sycp/sanlian",
  "sycp/mgk",
  "立即下载",
  "查看详情",
  "了解更多",
  "bilibili.ad.v1.",
  "AdsControlDto",
  "SourceContentDto",
];

// 硬特征：命中即视为广告子树
const DROP_MARKERS = [
  "sycp/sanlian",
  "sycp/app_icon",
  "sycp/mgk",
  "relatedvideo.cm",
  "united.player-video-detail.relatedvideo.cm",
  "from_spmid=united.player-video-detail.relatedvideo",
  "adtrack.qianwen.com",
  "cm.bilibili.com/ldad",
  "unet.quark.cn/v3/ad",
  // 冷启动 HAR 确认：部分横幅以 Any 包装的广告 DTO 下发，无 relatedvideo.cm
  "bilibili.ad.v1.AdsControlDto",
  "bilibili.ad.v1.SourceContentDto",
  "type.googleapis.com/bilibili.ad",
  // 播放页横幅「广告」角标颜色
  "#9499A0FF",
  "#757A81FF",
  // 商业卡监测/归因参数（重返未来等游戏卡裁剪后仍残留）
  "sycp_android_id",
  "sycp_ip_before",
  "sycp_ip=",
];

// 常见 CTA：立即下载 / 查看详情 / 了解更多（证券类多用查看详情）
const CTA_LABELS = ["立即下载", "查看详情", "了解更多", "立即打开", "去看看"];
const LABEL_AD = "广告";
const LABEL_PLAY = "播放";
// 嵌套裁剪后可能残留的小卡片上限（整页内容远大于此）
const RESIDUAL_AD_MAX_LEN = 25000;

function utf8Encode(text) {
  if (typeof TextEncoder !== "undefined") {
    return new TextEncoder().encode(text);
  }
  const utf8 = unescape(encodeURIComponent(text));
  const out = new Uint8Array(utf8.length);
  for (let i = 0; i < utf8.length; i++) {
    out[i] = utf8.charCodeAt(i);
  }
  return out;
}

function bytesIndexOf(haystack, needle) {
  if (typeof needle === "string") {
    needle = utf8Encode(needle);
  }
  if (!needle.length) {
    return 0;
  }
  outer: for (let i = 0; i <= haystack.length - needle.length; i++) {
    for (let j = 0; j < needle.length; j++) {
      if (haystack[i + j] !== needle[j]) {
        continue outer;
      }
    }
    return i;
  }
  return -1;
}

function bytesIncludes(haystack, needle) {
  return bytesIndexOf(haystack, needle) >= 0;
}

function hasScanMarker(data) {
  for (const m of SCAN_MARKERS) {
    if (bytesIncludes(data, m)) {
      return true;
    }
  }
  return false;
}

function hasCta(data) {
  for (const cta of CTA_LABELS) {
    if (bytesIncludes(data, cta)) {
      return true;
    }
  }
  return false;
}

function isResidualAdCard(data) {
  // 子字段被裁掉后，父卡片可能只剩标题+「广告·N播放」+ 封面 / App Store 落地
  if (data.length > RESIDUAL_AD_MAX_LEN) {
    return false;
  }
  const hasStore =
    bytesIncludes(data, "apps.apple.com") ||
    bytesIncludes(data, "itunes.apple.com");
  // 游戏/应用下载卡：商店链接 + 商业追踪/播放/隐私协议
  if (
    hasStore &&
    (bytesIncludes(data, "sycp") ||
      bytesIncludes(data, LABEL_PLAY) ||
      bytesIncludes(data, "隐私协议") ||
      bytesIncludes(data, "com."))
  ) {
    return true;
  }
  if (!bytesIncludes(data, LABEL_AD)) {
    return false;
  }
  if (
    bytesIncludes(data, LABEL_PLAY) &&
    (bytesIncludes(data, "vupload") ||
      bytesIncludes(data, "bfs/archive") ||
      bytesIncludes(data, "sycp/") ||
      hasCta(data))
  ) {
    return true;
  }
  // 广告负反馈文案多在商业卡上
  if (bytesIncludes(data, "sycp/mng") && bytesIncludes(data, "屏蔽广告")) {
    return true;
  }
  // 「评分 x.x/5」游戏软广横幅
  if (bytesIncludes(data, "评分") && (hasStore || bytesIncludes(data, "sycp"))) {
    return true;
  }
  return false;
}

function hasDropMarker(data) {
  for (const m of DROP_MARKERS) {
    if (bytesIncludes(data, m)) {
      return true;
    }
  }
  // CTA + 广告角标 / 商业素材 / 商店落地
  if (hasCta(data) && bytesIncludes(data, LABEL_AD)) {
    return true;
  }
  if (hasCta(data)) {
    if (
      bytesIncludes(data, "apps.apple.com") ||
      bytesIncludes(data, "itunes.apple.com") ||
      bytesIncludes(data, "adtrack.") ||
      bytesIncludes(data, "sycp/")
    ) {
      return true;
    }
  }
  if (bytesIncludes(data, "sycp/face") && bytesIncludes(data, LABEL_AD)) {
    return true;
  }
  if (bytesIncludes(data, "apps.apple.com") && bytesIncludes(data, LABEL_AD)) {
    return true;
  }
  if (isResidualAdCard(data)) {
    return true;
  }
  return false;
}

function toUint8Array(body) {
  if (!body) {
    return null;
  }
  if (body instanceof Uint8Array) {
    return body;
  }
  if (body instanceof ArrayBuffer) {
    return new Uint8Array(body);
  }
  if (typeof body === "string") {
    const out = new Uint8Array(body.length);
    for (let i = 0; i < body.length; i++) {
      out[i] = body.charCodeAt(i) & 0xff;
    }
    return out;
  }
  try {
    return new Uint8Array(body);
  } catch (e) {
    return null;
  }
}

function doneWithBytes(bytes) {
  if (
    typeof $response !== "undefined" &&
    Object.prototype.hasOwnProperty.call($response, "bodyBytes")
  ) {
    $done({ bodyBytes: bytes });
    return;
  }
  $done({
    body: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
  });
}

function readVarint(buf, i) {
  let result = 0;
  let shift = 0;
  while (i < buf.length) {
    const b = buf[i++];
    result |= (b & 0x7f) << shift;
    if (b < 0x80) {
      return [result, i];
    }
    shift += 7;
    if (shift > 35) {
      throw new Error("varint too long");
    }
  }
  throw new Error("truncated varint");
}

function writeVarint(n) {
  const out = [];
  n = n >>> 0;
  while (n > 0x7f) {
    out.push((n & 0x7f) | 0x80);
    n >>>= 7;
  }
  out.push(n & 0x7f);
  return out;
}

function cleanMessage(buf) {
  const out = [];
  let i = 0;
  const n = buf.length;
  while (i < n) {
    const start = i;
    let tag;
    try {
      [tag, i] = readVarint(buf, i);
    } catch (e) {
      for (let k = start; k < n; k++) out.push(buf[k]);
      break;
    }
    const fieldNumber = tag >>> 3;
    const wire = tag & 7;
    if (fieldNumber === 0) {
      for (let k = start; k < n; k++) out.push(buf[k]);
      break;
    }
    if (wire === 0) {
      let i2;
      try {
        [, i2] = readVarint(buf, i);
      } catch (e) {
        for (let k = start; k < n; k++) out.push(buf[k]);
        break;
      }
      for (let k = start; k < i2; k++) out.push(buf[k]);
      i = i2;
    } else if (wire === 1) {
      if (i + 8 > n) {
        for (let k = start; k < n; k++) out.push(buf[k]);
        break;
      }
      for (let k = start; k < i + 8; k++) out.push(buf[k]);
      i += 8;
    } else if (wire === 5) {
      if (i + 4 > n) {
        for (let k = start; k < n; k++) out.push(buf[k]);
        break;
      }
      for (let k = start; k < i + 4; k++) out.push(buf[k]);
      i += 4;
    } else if (wire === 2) {
      let length;
      let i2;
      try {
        [length, i2] = readVarint(buf, i);
      } catch (e) {
        for (let k = start; k < n; k++) out.push(buf[k]);
        break;
      }
      if (i2 + length > n) {
        for (let k = start; k < n; k++) out.push(buf[k]);
        break;
      }
      let data = buf.subarray(i2, i2 + length);
      i = i2 + length;
      if (hasDropMarker(data)) {
        const cleaned = cleanMessage(data);
        if (hasDropMarker(cleaned)) {
          continue;
        }
        data = cleaned;
      }
      const tagBytes = writeVarint(tag);
      const lenBytes = writeVarint(data.length);
      for (const b of tagBytes) out.push(b);
      for (const b of lenBytes) out.push(b);
      for (let k = 0; k < data.length; k++) out.push(data[k]);
    } else {
      for (let k = start; k < n; k++) out.push(buf[k]);
      break;
    }
  }
  return Uint8Array.from(out);
}

async function gunzip(bytes) {
  if (typeof $utils !== "undefined" && typeof $utils.ungzip === "function") {
    const res = $utils.ungzip(bytes);
    const arr = toUint8Array(res);
    if (arr) {
      return arr;
    }
  }
  if (typeof DecompressionStream !== "undefined") {
    const ab = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
    const stream = new Response(ab).body.pipeThrough(new DecompressionStream("gzip"));
    return new Uint8Array(await new Response(stream).arrayBuffer());
  }
  throw new Error("no gzip decompressor");
}

async function decodeGrpcFrames(raw) {
  const frames = [];
  let i = 0;
  while (i + 5 <= raw.length) {
    const compressed = raw[i];
    const length =
      ((raw[i + 1] << 24) | (raw[i + 2] << 16) | (raw[i + 3] << 8) | raw[i + 4]) >>> 0;
    i += 5;
    if (i + length > raw.length) {
      break;
    }
    let payload = raw.subarray(i, i + length);
    i += length;
    if (compressed === 1) {
      payload = await gunzip(payload);
    }
    frames.push(payload);
  }
  return frames;
}

function encodeGrpcUncompressed(messages) {
  let total = 0;
  for (const msg of messages) {
    total += 5 + msg.length;
  }
  const out = new Uint8Array(total);
  let o = 0;
  for (const msg of messages) {
    out[o++] = 0;
    const len = msg.length >>> 0;
    out[o++] = (len >>> 24) & 0xff;
    out[o++] = (len >>> 16) & 0xff;
    out[o++] = (len >>> 8) & 0xff;
    out[o++] = len & 0xff;
    out.set(msg, o);
    o += msg.length;
  }
  return out;
}

async function process(raw) {
  const frames = await decodeGrpcFrames(raw);
  if (!frames.length) {
    return null;
  }
  // 快路径：任一帧都没有协议特征则完全不改
  let anyMarker = false;
  for (const msg of frames) {
    if (msg.length >= 2 && msg[0] === 0x1f && msg[1] === 0x8b) {
      return null; // 解压失败，放行
    }
    if (hasScanMarker(msg)) {
      anyMarker = true;
      break;
    }
  }
  if (!anyMarker) {
    return null;
  }

  let changed = false;
  const cleanedFrames = frames.map((msg) => {
    const cleaned = cleanMessage(msg);
    if (cleaned.length !== msg.length) {
      changed = true;
    }
    return cleaned;
  });
  if (!changed) {
    return null;
  }
  return encodeGrpcUncompressed(cleanedFrames);
}

(async () => {
  const rawBody =
    typeof $response !== "undefined" &&
    typeof $response.bodyBytes !== "undefined" &&
    $response.bodyBytes
      ? $response.bodyBytes
      : $response.body;
  const bytes = toUint8Array(rawBody);
  if (!bytes || bytes.length < 10) {
    $done({});
    return;
  }
  try {
    const processed = await process(bytes);
    if (processed) {
      console.log(
        `哔哩哔哩播放页banner-lite：${bytes.length} -> ${processed.length}`,
      );
      doneWithBytes(processed);
    } else {
      $done({});
    }
  } catch (error) {
    console.log(`哔哩哔哩播放页banner-lite：失败放行（${error}）`);
    $done({});
  }
})();
