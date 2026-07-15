let responseBody = $response.body;

try {
  const payload = JSON.parse(responseBody);
  if (payload && payload.data && typeof payload.data === "object") {
    delete payload.data.boot_page;

    const adSections = [
      "noticeList",
      "lower_right_corner_ad",
      "banner",
      "block_ad",
      "question_ad",
    ];

    for (const sectionName of adSections) {
      const section = payload.data[sectionName];
      if (section && typeof section === "object" && Array.isArray(section.ads)) {
        section.ads = [];
      }
    }

    responseBody = JSON.stringify(payload);
  }
} catch (error) {
  console.log(`医考帮去广告：响应不是有效 JSON，已保留原响应（${error}）`);
}

$done({ body: responseBody });
