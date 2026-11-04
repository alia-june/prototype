import { requestForWire } from "./protocol.mjs";

import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const DEFAULT_ROOT = resolve(HERE, "../..");

export function runPythonDataPlane(request, options = {}) {
  const python = options.python ?? process.env.PYTHON_BIN ?? "python";
  const root = options.root ?? DEFAULT_ROOT;
  const worker = resolve(root, "scripts/sc0_worker.py");

  const localRequest = {
    ...request,
    allow_web: false,
    allow_llm: false,
  };

  return new Promise((resolvePromise, reject) => {
    const child = spawn(python, [worker], {
      cwd: root,
      stdio: ["pipe", "pipe", "pipe"],
      windowsHide: true,
    });
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`python data plane exited ${code}: ${stderr.trim()}`));
        return;
      }
      try {
        resolvePromise(JSON.parse(stdout));
      } catch (error) {
        reject(new Error(`invalid python data-plane JSON: ${error.message}; stderr=${stderr.trim()}`));
      }
    });
    child.stdin.end(JSON.stringify(requestForWire(localRequest)));
  });
}


export function probePythonCapabilities(options = {}) {
  const python = options.python ?? process.env.PYTHON_BIN ?? "python";
  const root = options.root ?? DEFAULT_ROOT;
  const worker = resolve(root, "scripts/sc0_worker.py");
  return new Promise((resolvePromise, reject) => {
    const child = spawn(python, [worker], { cwd: root, stdio: ["pipe", "pipe", "pipe"], windowsHide: true });
    let stdout = ""; let stderr = "";
    child.stdout.setEncoding("utf8"); child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0) { reject(new Error(`python capability probe exited ${code}: ${stderr.trim()}`)); return; }
      try { resolvePromise(JSON.parse(stdout)); }
      catch (error) { reject(new Error(`invalid capability JSON: ${error.message}`)); }
    });
    child.stdin.end(JSON.stringify({ $control: "capabilities" }));
  });
}

export function benchmarkPythonBackends(options = {}) {
  const python = options.python ?? process.env.PYTHON_BIN ?? "python";
  const root = options.root ?? DEFAULT_ROOT;
  const worker = resolve(root, "scripts/sc0_worker.py");
  const repeats = options.repeats ?? 3;
  const sizes = options.sizes ?? [64, 1024, 16384];
  return new Promise((resolvePromise, reject) => {
    const child = spawn(python, [worker], { cwd: root, stdio: ["pipe", "pipe", "pipe"], windowsHide: true });
    let stdout = ""; let stderr = "";
    child.stdout.setEncoding("utf8"); child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0) { reject(new Error(`python benchmark exited ${code}: ${stderr.trim()}`)); return; }
      try { resolvePromise(JSON.parse(stdout)); }
      catch (error) { reject(new Error(`invalid benchmark JSON: ${error.message}`)); }
    });
    child.stdin.end(JSON.stringify({ $control: "benchmark", repeats, sizes }));
  });
}
