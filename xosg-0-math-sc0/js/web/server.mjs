import http from "node:http";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MathSC0ControlPlane } from "../src/control-plane.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../..");
const PUBLIC = path.join(HERE, "public");
const CONTRACT_PATH = path.join(ROOT, "protocol", "operation_contracts.v0.6.json");
const MAX_BODY_BYTES = 2 * 1024 * 1024;

const TYPES = new Map([
  [".html", "text/html; charset=utf-8"],
  [".js", "text/javascript; charset=utf-8"],
  [".css", "text/css; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".svg", "image/svg+xml"],
]);

function json(res, status, body) {
  const data = JSON.stringify(body);
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "content-length": Buffer.byteLength(data),
    "cache-control": "no-store",
    "x-content-type-options": "nosniff",
  });
  res.end(data);
}

async function readJson(req) {
  let size = 0;
  const chunks = [];
  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) {
      const error = new Error(`request body exceeds ${MAX_BODY_BYTES} bytes`);
      error.statusCode = 413;
      throw error;
    }
    chunks.push(chunk);
  }
  const text = Buffer.concat(chunks).toString("utf8");
  if (!text.trim()) throw Object.assign(new Error("request body must contain JSON"), { statusCode: 400 });
  try {
    return JSON.parse(text);
  } catch (error) {
    throw Object.assign(new Error(`invalid JSON: ${error.message}`), { statusCode: 400 });
  }
}

async function serveStatic(reqPath, res) {
  const decoded = decodeURIComponent(reqPath === "/" ? "/index.html" : reqPath);
  const candidate = path.resolve(PUBLIC, `.${decoded}`);
  if (!candidate.startsWith(`${PUBLIC}${path.sep}`)) {
    json(res, 403, { status: "failed", error: "forbidden path" });
    return;
  }
  try {
    const stat = await fs.stat(candidate);
    if (!stat.isFile()) throw new Error("not file");
    const data = await fs.readFile(candidate);
    res.writeHead(200, {
      "content-type": TYPES.get(path.extname(candidate)) ?? "application/octet-stream",
      "content-length": data.length,
      "cache-control": "no-cache",
      "x-content-type-options": "nosniff",
      "content-security-policy": "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    });
    res.end(data);
  } catch {
    json(res, 404, { status: "failed", error: "not found" });
  }
}

export function createAppServer({ controlPlane = new MathSC0ControlPlane({ root: ROOT }) } = {}) {
  return http.createServer(async (req, res) => {
    try {
      const url = new URL(req.url ?? "/", "http://localhost");
      if (req.method === "GET" && url.pathname === "/api/health") {
        json(res, 200, { status: "ok", service: "MATH.SC-0 JavaScript Front End", ui_version: "0.5.0", default_external_providers: { web: false, llm: false } });
        return;
      }
      if (req.method === "GET" && url.pathname === "/api/contracts") {
        const contract = JSON.parse(await fs.readFile(CONTRACT_PATH, "utf8"));
        json(res, 200, contract);
        return;
      }
      if (req.method === "POST" && url.pathname === "/api/compute") {
        const request = await readJson(req);
        const result = await controlPlane.compute(request);
        json(res, result.status === "failed" ? 422 : 200, result);
        return;
      }
      if (req.method !== "GET") {
        json(res, 405, { status: "failed", error: "method not allowed" });
        return;
      }
      await serveStatic(url.pathname, res);
    } catch (error) {
      const boundaryStatus = error.statusCode ?? (["ContractError", "RangeError", "TypeError"].includes(error.name) ? 422 : 500);
      json(res, boundaryStatus, {
        status: "failed",
        error: `${error.name}: ${error.message}`,
        error_code: "WEB_FRONTEND_BOUNDARY_FAILURE",
      });
    }
  });
}

export async function startServer({ host = process.env.XOSG_SC0_HOST ?? "127.0.0.1", port = Number(process.env.XOSG_SC0_PORT ?? 8787) } = {}) {
  const server = createAppServer();
  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, host, resolve);
  });
  const address = server.address();
  const actualPort = typeof address === "object" && address ? address.port : port;
  process.stdout.write(`MATH.SC-0 web front end: http://${host}:${actualPort}\n`);
  return server;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  startServer().catch((error) => {
    process.stderr.write(`${error.stack ?? error}\n`);
    process.exitCode = 1;
  });
}
