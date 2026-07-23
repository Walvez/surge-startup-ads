// 仅移除播放页「视频下方」banner 广告（ViewUnite gRPC protobuf）。
// 窄范围：不处理评论/弹幕/动态/搜索/首页，避免全量 B 站去广告模块。
//
// HAR 依据：广告在 bilibili.app.viewunite.v1.View/View 压缩帧内，
// 特征含 sycp/sanlian|mgk、relatedvideo.cm、立即下载 + App Store/监测链 等。

const AD_MARKERS = [
  "sycp/sanlian",
  "sycp/app_icon",
  "sycp/mgk",
  "relatedvideo.cm",
  "united.player-video-detail.relatedvideo.cm",
  "from_spmid=united.player-video-detail.relatedvideo",
  "adtrack.qianwen.com",
  "cm.bilibili.com/ldad",
  "unet.quark.cn/v3/ad",
];

const CTA_DOWNLOAD = "立即下载";
const LABEL_AD = "广告";

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
  if (typeof $response !== "undefined" && Object.prototype.hasOwnProperty.call($response, "bodyBytes")) {
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

function hasAdMarker(data) {
  for (const marker of AD_MARKERS) {
    if (bytesIncludes(data, marker)) {
      return true;
    }
  }
  if (bytesIncludes(data, CTA_DOWNLOAD)) {
    if (
      bytesIncludes(data, "apps.apple.com") ||
      bytesIncludes(data, "itunes.apple.com") ||
      bytesIncludes(data, "adtrack.") ||
      bytesIncludes(data, "sycp/") ||
      bytesIncludes(data, LABEL_AD)
    ) {
      return true;
    }
  }
  if (bytesIncludes(data, "sycp/face") && bytesIncludes(data, LABEL_AD)) {
    return true;
  }
  if (bytesIncludes(data, "sycp/mng") && bytesIncludes(data, "屏蔽广告")) {
    return true;
  }
  if (bytesIncludes(data, "apps.apple.com") && bytesIncludes(data, LABEL_AD)) {
    return true;
  }
  return false;
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
      if (hasAdMarker(data)) {
        const cleaned = cleanMessage(data);
        if (hasAdMarker(cleaned)) {
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
  throw new Error("no gzip decompressor in this script runtime");
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

async function processGrpcBody(raw) {
  const frames = await decodeGrpcFrames(raw);
  if (!frames.length) {
    return null;
  }
  let changed = false;
  const cleanedFrames = frames.map((msg) => {
    // 仍是 gzip 魔数说明解压失败
    if (msg.length >= 2 && msg[0] === 0x1f && msg[1] === 0x8b) {
      return msg;
    }
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
    const processed = await processGrpcBody(bytes);
    if (processed) {
      console.log(
        `哔哩哔哩播放页下方广告：protobuf ${bytes.length} -> ${processed.length}`,
      );
      doneWithBytes(processed);
    } else {
      $done({});
    }
  } catch (error) {
    console.log(`哔哩哔哩播放页下方广告：处理失败，已保留原响应（${error}）`);
    $done({});
  }
})();
