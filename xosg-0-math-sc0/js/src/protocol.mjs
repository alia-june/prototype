import { CONTRACT_VERSION, PROTOCOL_VERSION, validateOperationRequest } from "./contracts.mjs";

export const MODES = new Set(["auto", "exact", "float64", "high_precision", "interval"]);

export function normalizeRequest(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) throw new TypeError("request must be an object");
  if (typeof input.operation !== "string" || input.operation.trim() === "") throw new TypeError("operation must be a non-empty string");
  if (!Array.isArray(input.operands)) throw new TypeError("operands must be an array");

  const mode = input.mode ?? "auto";
  if (!MODES.has(mode)) throw new RangeError(`unsupported numeric mode: ${mode}`);
  const precision = input.precision ?? null;
  if (precision !== null && (!Number.isInteger(precision) || precision < 1)) throw new RangeError("precision must be a positive integer or null");
  const tolerance = input.tolerance ?? 1e-12;
  if (typeof tolerance !== "number" || Number.isNaN(tolerance) || tolerance < 0) throw new RangeError("tolerance must be a non-negative number");

  const base = Object.freeze({
    protocol_version: input.protocol_version ?? PROTOCOL_VERSION,
    contract_version: input.contract_version ?? CONTRACT_VERSION,
    operation: input.operation,
    operands: input.operands,
    mode,
    precision,
    tolerance,
    deterministic: input.deterministic ?? true,
    allow_web: input.allow_web ?? true,
    allow_llm: input.allow_llm ?? true,
    metadata: input.metadata ?? {},
  });

  if (base.protocol_version !== PROTOCOL_VERSION) throw new RangeError(`unsupported protocol version: ${base.protocol_version}`);
  if (base.contract_version !== CONTRACT_VERSION) throw new RangeError(`unsupported contract version: ${base.contract_version}`);
  const validation = validateOperationRequest(base, { allowUncontracted: true });
  return Object.freeze({
    ...validation.request,
    _contract: Object.freeze({
      contract_state: validation.contract_state,
      contract_version: validation.contract_version,
      protocol_version: validation.protocol_version,
      operation_id: validation.operation_id,
      input_shapes: validation.input_shapes,
      scalar_count: validation.scalar_count,
    }),
  });
}

export function requestForWire(request) {
  const { _contract, ...wire } = request;
  return wire;
}

export function fallbackResult({ value, backend, status, algorithm, source = null }) {
  return {
    value,
    status,
    backend,
    algorithm,
    verified: false,
    exact: false,
    tolerance: null,
    error: null,
    error_code: null,
    trace: [],
    metadata: source ? { source } : {},
    authority: backend === "web" ? "external_source" : "heuristic",
    control_plane: "javascript"
  };
}
