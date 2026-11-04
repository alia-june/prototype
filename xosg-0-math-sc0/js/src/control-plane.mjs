import { normalizeRequest, fallbackResult } from "./protocol.mjs";
import { runPythonDataPlane } from "./python-worker.mjs";

/**
 * MATH.SC-0 global authority/fallback controller.
 *
 * Global order:
 *   1. Python deterministic data plane
 *      exact -> high_precision -> accelerator -> open_compute -> native -> numpy -> cpu
 *   2. web provider
 *   3. LLM provider (strict last resort)
 */
export class MathSC0ControlPlane {
  constructor({ python = undefined, root = undefined, localRunner = undefined, webProvider = null, llmProvider = null } = {}) {
    this.python = python;
    this.root = root;
    this.localRunner = localRunner ?? ((request) => runPythonDataPlane(request, { python: this.python, root: this.root }));
    this.webProvider = webProvider;
    this.llmProvider = llmProvider;
  }

  async compute(input) {
    const request = normalizeRequest(input);
    const trace = [];

    try {
      trace.push("dispatch deterministic_local");
      const local = await this.localRunner(request);
      if (local?.status && local.status !== "failed") {
        local.trace = [...trace, ...(local.trace ?? [])];
        local.control_plane = "javascript";
        return local;
      }
      trace.push(`fail deterministic_local: ${local?.error ?? "no backend completed request"}`);
    } catch (error) {
      trace.push(`fail deterministic_local: ${error.name}: ${error.message}`);
    }

    if (request.allow_web && this.webProvider) {
      try {
        trace.push("dispatch web");
        const raw = await this.webProvider(request);
        const result = normalizeExternal(raw, "web");
        result.metadata = { ...(result.metadata ?? {}), ...request._contract };
        result.trace = [...trace, ...(result.trace ?? [])];
        return result;
      } catch (error) {
        trace.push(`fail web: ${error.name}: ${error.message}`);
      }
    } else {
      trace.push("skip web: disabled or unavailable");
    }

    if (request.allow_llm && this.llmProvider) {
      try {
        trace.push("dispatch llm_fallback");
        const raw = await this.llmProvider(request);
        const result = normalizeExternal(raw, "llm_fallback");
        result.metadata = { ...(result.metadata ?? {}), ...request._contract };
        // Hard safety invariant: LLM output cannot assert computational verification.
        result.status = "llm_inferred";
        result.verified = false;
        result.authority = "heuristic";
        result.trace = [...trace, ...(result.trace ?? [])];
        return result;
      } catch (error) {
        trace.push(`fail llm_fallback: ${error.name}: ${error.message}`);
      }
    } else {
      trace.push("skip llm_fallback: disabled or unavailable");
    }

    return {
      value: null,
      status: "failed",
      backend: "none",
      algorithm: "",
      verified: false,
      exact: false,
      tolerance: request.tolerance,
      error: "no backend completed the request",
      error_code: "NO_BACKEND_COMPLETED",
      trace,
      metadata: { ...request._contract },
      authority: "none",
      control_plane: "javascript"
    };
  }
}

function normalizeExternal(raw, backend) {
  if (raw && typeof raw === "object" && !Array.isArray(raw) && Object.hasOwn(raw, "value")) {
    return {
      ...raw,
      backend,
      status: backend === "web" ? "web_sourced" : "llm_inferred",
      verified: false,
      exact: false,
      authority: backend === "web" ? "external_source" : "heuristic",
      control_plane: "javascript",
    };
  }
  return fallbackResult({
    value: raw,
    backend,
    status: backend === "web" ? "web_sourced" : "llm_inferred",
    algorithm: backend === "web" ? "external.web_provider" : "external.llm_provider",
  });
}
