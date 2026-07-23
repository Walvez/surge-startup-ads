// 哔哩哔哩开屏：返回结构完整的空数据，避免 reject-dict 的 "{}" 被客户端当成失败后继续展示本地缓存开屏。
// 覆盖 show / list / event/list2 / brand/list。

const EMPTY_SHOW = {
  code: 0,
  message: "OK",
  ttl: 1,
  data: {
    show: [],
  },
};

const EMPTY_LIST = {
  code: 0,
  message: "OK",
  ttl: 1,
  data: {
    max_time: 0,
    min_interval: 86400,
    pull_interval: 86400,
    keep_ids: [],
    list: [],
    show: [],
  },
};

const EMPTY_EVENT = {
  code: 0,
  message: "OK",
  ttl: 1,
  data: {
    event_list: [],
  },
};

const EMPTY_BRAND = {
  code: 0,
  message: "OK",
  ttl: 1,
  data: {
    pull_interval: 86400,
    forcibly: 0,
    rule: 0,
    list: [],
    preload: [],
    has_new_splash_set: 0,
  },
};

function pickEmptyBody(url) {
  const u = String(url || "");
  if (u.includes("/splash/show")) {
    return EMPTY_SHOW;
  }
  if (u.includes("/splash/event/list2") || u.includes("/splash/event/list")) {
    return EMPTY_EVENT;
  }
  if (u.includes("/splash/brand/list")) {
    return EMPTY_BRAND;
  }
  // list 及未知 splash 子路径
  return EMPTY_LIST;
}

const url =
  (typeof $request !== "undefined" && $request && $request.url) ||
  (typeof $request !== "undefined" && $request && $request.URL) ||
  "";

const body = JSON.stringify(pickEmptyBody(url));
console.log(`哔哩哔哩开屏：返回空结构 ${url.split("?")[0] || ""}`);
$done({ body });
