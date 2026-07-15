let responseBody = $response.body;

try {
  const payload = JSON.parse(responseBody);
  if (payload && payload.data && typeof payload.data === "object") {
    delete payload.data.boot_page;
    responseBody = JSON.stringify(payload);
  }
} catch (error) {
  console.log(`医考帮去开屏：响应不是有效 JSON，已保留原响应（${error}）`);
}

$done({ body: responseBody });
