// 仅移除推荐信息流中的「创作推广」(ad_av) 与「会员购」(ad_web_s) 卡片。
// 不处理开屏、banner 轮播、搜索、动态、评论或其它接口，避免全量去广告脚本拖慢 App。

const TARGET_CARD_GOTOS = new Set(["ad_av", "ad_web_s"]);
const TARGET_BADGE_TEXT = ["创作推广", "会员购"];

function collectText(value, out) {
  if (value == null) {
    return;
  }
  if (typeof value === "string") {
    if (value) {
      out.push(value);
    }
    return;
  }
  if (Array.isArray(value)) {
    for (const item of value) {
      collectText(item, out);
    }
    return;
  }
  if (typeof value === "object") {
    for (const key of ["text", "title", "desc", "name", "label"]) {
      if (typeof value[key] === "string" && value[key]) {
        out.push(value[key]);
      }
    }
  }
}

function hasTargetBadge(item) {
  const texts = [];
  collectText(item.desc, texts);
  collectText(item.desc_button, texts);
  collectText(item.cover_right_text, texts);
  collectText(item.goto_icon, texts);
  collectText(item.badges, texts);
  collectText(item.badge, texts);
  collectText((item.ad_info || {}).creative_content, texts);

  const joined = texts.join(" ");
  return TARGET_BADGE_TEXT.some((badge) => joined.includes(badge));
}

function isTargetFeedAd(item) {
  if (!item || typeof item !== "object") {
    return false;
  }

  const cardGoto = String(item.card_goto || "");
  if (TARGET_CARD_GOTOS.has(cardGoto)) {
    return true;
  }

  // 兜底：个别版本 card_goto 变化时，仍按角标文案识别这两类广告。
  if (item.card_type === "cm_v2" && hasTargetBadge(item)) {
    return true;
  }

  return false;
}

function filterFeedItems(items) {
  if (!Array.isArray(items)) {
    return items;
  }
  return items.filter((item) => !isTargetFeedAd(item));
}

let responseBody = $response.body;

try {
  const payload = JSON.parse(responseBody);
  if (payload && payload.data && Array.isArray(payload.data.items)) {
    const before = payload.data.items.length;
    payload.data.items = filterFeedItems(payload.data.items);
    const removed = before - payload.data.items.length;
    if (removed > 0) {
      console.log(`哔哩哔哩信息流：移除 ${removed} 条创作推广/会员购卡片`);
    }
    responseBody = JSON.stringify(payload);
  }
} catch (error) {
  console.log(`哔哩哔哩信息流：处理失败，已保留原响应（${error}）`);
}

$done({ body: responseBody });
