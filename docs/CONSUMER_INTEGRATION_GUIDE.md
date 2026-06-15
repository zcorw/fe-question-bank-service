# Consumer Integration Guide

This guide is for applications that consume FE Question Bank Service through
HTTP instead of reading `fe_siken_questions.sqlite` or image files directly.

## Service Endpoints

Runtime service:

```text
http://<service-host>:8000
```

Common read-only endpoints:

```text
GET  /health
GET  /keywords
GET  /questions/candidates
POST /questions/candidates/search
GET  /questions/by-url?url=<question-url>
GET  /questions/{questionId}
POST /questions/details/batch
GET  /assets/fe-siken/<asset-path>
```

Admin endpoints are maintenance-only and require `Authorization: Bearer
<ADMIN_API_TOKEN>`. Consumer apps should normally use Runtime endpoints only.

## Docker Compose Integration

Use this mode when the consuming app runs in Docker Compose on the same VPS.
Both stacks must join the same external Docker network.

Create the shared network once:

```bash
docker network inspect fe-shared >/dev/null 2>&1 || docker network create fe-shared
```

Question bank service compose:

```yaml
services:
  question-bank-runtime:
    networks:
      - fe-shared

networks:
  fe-shared:
    external: true
```

Consumer app compose:

```yaml
services:
  web:
    environment:
      QUESTION_BANK_SERVICE_URL: http://question-bank-runtime:8000
    networks:
      - default
      - fe-shared

networks:
  fe-shared:
    external: true
```

Inside the consumer container, verify service access:

```bash
curl -fsS http://question-bank-runtime:8000/health
```

Do not use the host-published port from one container to another when both
containers are on `fe-shared`. Use the Docker service name
`question-bank-runtime`.

## Local Network Integration

Use this mode when the consumer app runs outside Docker or on another host that
can reach the VPS.

On the question bank host, publish Runtime to the intended host interface:

```env
QUESTION_BANK_RUNTIME_HOST=127.0.0.1
QUESTION_BANK_RUNTIME_PORT=8124
```

Use `127.0.0.1` when only local processes or a reverse proxy on the same host
should reach the service. Use `0.0.0.0` only when the service must bind to all
host interfaces and your firewall/reverse proxy rules are ready.

Consumer configuration on the same host:

```env
QUESTION_BANK_SERVICE_URL=http://127.0.0.1:8124
```

Verify:

```bash
curl -fsS http://127.0.0.1:8124/health
```

For another host on the private network, use the private host address or an
internal DNS name:

```env
QUESTION_BANK_SERVICE_URL=http://10.0.0.20:8124
```

Do not expose Admin API publicly. Keep Runtime read-only and put external access
behind a trusted reverse proxy if it must cross host boundaries.

## Query Flow

Typical quiz creation flow:

1. Call `/questions/candidates` or `/questions/candidates/search`.
2. Pick question URLs in the consumer app.
3. Call `/questions/details/batch` with those URLs.
4. Render `questionText`, `choices`, and `images`.
5. Request answers only when needed by setting `includeAnswer=true`.

Example batch detail request:

```bash
curl -fsS -X POST "$QUESTION_BANK_SERVICE_URL/questions/details/batch" \
  -H "content-type: application/json" \
  -d '{
    "urls": ["https://www.fe-siken.com/kakomon/sample/q1.html"],
    "includeAnswer": false,
    "includeExplanation": false
  }'
```

Image references in responses should be treated as web paths, not filesystem
paths. Use `publicPath` or Markdown image paths such as:

```text
/assets/fe-siken/07_haru/a6/06.png
```

## Browser Image Proxy

If the consumer app renders HTML in a browser, the browser usually cannot reach
Docker-internal names such as `question-bank-runtime`. In that case, the
consumer app must proxy image requests.

Recommended browser-facing path:

```text
https://<consumer-domain>/assets/fe-siken/<asset-path>
```

Server-side proxy target:

```text
$QUESTION_BANK_SERVICE_URL/assets/fe-siken/<asset-path>
```

For Docker Compose consumers, this usually means:

```text
browser -> https://<consumer-domain>/assets/fe-siken/q.png
consumer web container -> http://question-bank-runtime:8000/assets/fe-siken/q.png
```

Do not return `http://question-bank-runtime:8000/...` directly to browser code.
That hostname is only resolvable inside the Docker network.

## Next.js Proxy Example

```ts
export const runtime = "nodejs";

type RouteContext = {
  params: Promise<{ path: string[] }> | { path: string[] };
};

export async function GET(_request: Request, context: RouteContext) {
  const { path } = await context.params;
  const baseUrl = process.env.QUESTION_BANK_SERVICE_URL?.replace(/\/+$/, "");

  if (!baseUrl) {
    return new Response("QUESTION_BANK_SERVICE_URL is not configured.", {
      status: 500,
    });
  }

  if (!path.every((segment) => segment && segment !== "." && segment !== "..")) {
    return new Response("Invalid asset path.", { status: 400 });
  }

  const assetPath = path.map(encodeURIComponent).join("/");
  const upstream = await fetch(`${baseUrl}/assets/fe-siken/${assetPath}`);

  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "content-type": upstream.headers.get("content-type") ?? "application/octet-stream",
    },
  });
}
```

Route location:

```text
src/app/assets/fe-siken/[...path]/route.ts
```

## Express Proxy Example

```ts
app.get("/assets/fe-siken/*", async (req, res) => {
  const baseUrl = process.env.QUESTION_BANK_SERVICE_URL?.replace(/\/+$/, "");
  if (!baseUrl) {
    res.status(500).send("QUESTION_BANK_SERVICE_URL is not configured.");
    return;
  }

  const assetPath = req.params[0];
  if (assetPath.split("/").some((segment) => !segment || segment === "." || segment === "..")) {
    res.status(400).send("Invalid asset path.");
    return;
  }

  const upstream = await fetch(`${baseUrl}/assets/fe-siken/${assetPath}`);
  res.status(upstream.status);
  const contentType = upstream.headers.get("content-type");
  if (contentType) {
    res.setHeader("content-type", contentType);
  }
  res.send(Buffer.from(await upstream.arrayBuffer()));
});
```

## Markdown Image URL Handling

Consumer apps should normalize image `src` values before rendering. If incoming
question Markdown contains an internal absolute URL, rewrite it to the browser
proxy path.

```ts
function normalizeQuestionImageSrc(src: string): string {
  const marker = "/assets/fe-siken/";
  const index = src.indexOf(marker);
  return index === -1 ? src : src.slice(index);
}
```

Examples:

```text
/assets/fe-siken/r7/q1.png
  -> /assets/fe-siken/r7/q1.png

http://question-bank-runtime:8000/assets/fe-siken/r7/q1.png
  -> /assets/fe-siken/r7/q1.png
```

## Verification Checklist

Docker consumer:

```bash
docker exec <consumer-container> printenv QUESTION_BANK_SERVICE_URL
docker exec <consumer-container> curl -fsS http://question-bank-runtime:8000/health
```

Host/local consumer:

```bash
curl -fsS "$QUESTION_BANK_SERVICE_URL/health"
```

Image proxy:

```bash
curl -fsS "$QUESTION_BANK_SERVICE_URL/assets/fe-siken/<known-image-path>" --output /tmp/qbs-image
curl -fsS "https://<consumer-domain>/assets/fe-siken/<known-image-path>" --output /tmp/consumer-image
```

The two downloaded files should both be non-empty. If the first command works
but the second fails, the problem is in the consumer app's proxy or public
routing. If the first command fails, check `HOST_ASSET_DIR`,
`QUESTION_ASSET_ROOT`, and whether the image file exists in the question bank
service deployment.

## Common Mistakes

- Using `localhost` inside a container to reach the question bank service.
  `localhost` points to the current container, not the Runtime container.
- Returning `http://question-bank-runtime:8000/...` to browser code.
- Mounting question image directories into consumer apps after migration.
- Backing up SQLite without backing up `HOST_ASSET_DIR`.
- Enabling Admin API for normal consumer runtime traffic.
