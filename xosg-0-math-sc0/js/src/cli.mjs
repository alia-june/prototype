#!/usr/bin/env node
import { MathSC0ControlPlane } from "./control-plane.mjs";

async function readStdin() {
  let text = "";
  process.stdin.setEncoding("utf8");
  for await (const chunk of process.stdin) text += chunk;
  return text;
}

try {
  const text = process.argv[2] ?? await readStdin();
  if (!text.trim()) throw new Error("expected request JSON as argument or stdin");
  const request = JSON.parse(text);
  // CLI intentionally has no implicit network or LLM provider. Embedders inject them.
  const result = await new MathSC0ControlPlane().compute(request);
  process.stdout.write(`${JSON.stringify(result)}\n`);
} catch (error) {
  process.stdout.write(`${JSON.stringify({
    value: null,
    status: "failed",
    backend: "javascript_cli",
    verified: false,
    error: `${error.name}: ${error.message}`,
    error_code: "CONTROL_PLANE_BOUNDARY_FAILURE",
    trace: ["javascript CLI boundary failure"],
    authority: "none",
    control_plane: "javascript"
  })}\n`);
  process.exitCode = 1;
}
