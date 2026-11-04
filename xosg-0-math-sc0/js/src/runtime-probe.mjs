import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

function probe(command, args) {
  const r = spawnSync(command, args, { encoding: "utf8", windowsHide: true });
  if (r.error) return { available: false, error: r.error.message };
  return { available: r.status === 0, version: (r.stdout || r.stderr).trim().split(/\r?\n/)[0] };
}

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../..");
const nativeLib = process.platform === "darwin"
  ? resolve(root, "build/libsc0native.dylib")
  : process.platform === "win32"
    ? resolve(root, "build/sc0native.dll")
    : resolve(root, "build/libsc0native.so");

const report = {
  node: { available: true, version: process.version, platform: process.platform, arch: process.arch },
  python: probe(process.env.PYTHON_BIN ?? "python", ["--version"]),
  c: probe(process.env.CC ?? "gcc", ["--version"]),
  cpp: probe(process.env.CXX ?? "g++", ["--version"]),
  native_library: { available: existsSync(nativeLib), path: nativeLib },
};
console.log(JSON.stringify(report, null, 2));
