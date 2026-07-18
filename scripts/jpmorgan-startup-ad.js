let responseBody = $response.body;

try {
  const headers = $request.headers || {};
  const userAgentHeader = Object.keys(headers).find(
    (name) => name.toLowerCase() === "user-agent",
  );
  const userAgent = userAgentHeader ? String(headers[userAgentHeader]) : "";

  if (/^TKApp_Dis\//i.test(userAgent)) {
    const payload = JSON.parse(responseBody);
    if (payload && Array.isArray(payload.data)) {
      payload.data = [];
      responseBody = JSON.stringify(payload);
    }
  }
} catch (error) {
  console.log(`摩根资产管理去开屏：处理失败，已保留原响应（${error}）`);
}

$done({ body: responseBody });
