import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CONTRACT_PATH = path.resolve(HERE, "../../protocol/operation_contracts.v0.6.json");
const CONTRACT = JSON.parse(fs.readFileSync(CONTRACT_PATH, "utf8"));
const BY_ID = new Map(Object.entries(CONTRACT.operations).map(([name, spec]) => [spec.operation_id, name]));

export const CONTRACT_VERSION = CONTRACT.contract_version;
export const PROTOCOL_VERSION = CONTRACT.protocol_version;
export const RESOURCE_LIMITS = Object.freeze({ ...CONTRACT.resource_limits });

export class ContractError extends RangeError {
  constructor(message) {
    super(message);
    this.name = "ContractError";
  }
}

export function resolveOperation(operation) {
  if (Object.hasOwn(CONTRACT.operations, operation)) {
    return { name: operation, spec: CONTRACT.operations[operation] };
  }
  const name = BY_ID.get(operation);
  return name ? { name, spec: CONTRACT.operations[name] } : null;
}

export function validateOperationRequest(request, { allowUncontracted = false } = {}) {
  validateGeneric(request);
  const resolved = resolveOperation(request.operation);
  if (!resolved) {
    if (!allowUncontracted) throw new ContractError(`uncontracted operation: ${request.operation}`);
    return Object.freeze({
      request,
      contract_state: "uncontracted",
      contract_version: CONTRACT_VERSION,
      protocol_version: PROTOCOL_VERSION,
      operation_id: null,
      input_shapes: request.operands.map((x) => shapeOf(x)),
      scalar_count: scalarCount(request.operands),
    });
  }

  const normalized = Object.freeze({ ...request, operation: resolved.name });
  validateKnown(normalized, resolved.spec);
  return Object.freeze({
    request: normalized,
    contract_state: "contracted",
    contract_version: CONTRACT_VERSION,
    protocol_version: PROTOCOL_VERSION,
    operation_id: resolved.spec.operation_id,
    input_shapes: normalized.operands.map((x) => shapeOf(x)),
    scalar_count: scalarCount(normalized.operands),
  });
}

function validateGeneric(request) {
  if (request.precision !== null && request.precision > RESOURCE_LIMITS.max_precision_digits) {
    throw new ContractError(`precision exceeds limit ${RESOURCE_LIMITS.max_precision_digits}`);
  }
  if (request.tolerance < 0 || request.tolerance > RESOURCE_LIMITS.max_tolerance) {
    throw new ContractError(`tolerance must be between 0 and ${RESOURCE_LIMITS.max_tolerance}`);
  }
  const count = scalarCount(request.operands);
  if (count > RESOURCE_LIMITS.max_scalar_count) {
    throw new ContractError(`scalar count ${count} exceeds limit ${RESOURCE_LIMITS.max_scalar_count}`);
  }
  for (const operand of request.operands) {
    shapeOf(operand);
    validateStringLengths(operand, RESOURCE_LIMITS.max_numeric_string_chars ?? 10000);
    validateScalars(operand, request.mode);
  }
}

function validateKnown(request, spec) {
  if (!spec.arity.includes(request.operands.length)) {
    throw new ContractError(`${request.operation} expects arity ${JSON.stringify(spec.arity)}, got ${request.operands.length}`);
  }
  if (!spec.modes.includes(request.mode)) {
    throw new ContractError(`mode ${request.mode} is not permitted for ${request.operation}`);
  }

  const shapes = request.operands.map((x) => shapeOf(x));
  switch (spec.signature) {
    case "same_shape_binary":
      if (!sameShape(shapes[0], shapes[1])) throw new ContractError(`${request.operation} operands must have identical shapes`);
      if (!spec.ranks.includes(shapes[0].length)) throw new ContractError(`${request.operation} rank ${shapes[0].length} is not permitted`);
      break;
    case "scalar_binary":
      if (shapes.some((s) => s.length !== 0)) throw new ContractError(`${request.operation} requires two scalar operands`);
      break;
    case "scalar_unary":
      if (shapes.length !== 1 || shapes[0].length !== 0) throw new ContractError(`${request.operation} requires one scalar operand`);
      break;
    case "log_scalar":
      if (shapes.some((s) => s.length !== 0)) throw new ContractError("log requires scalar operands");
      break;
    case "vector_reduction":
      if (shapes[0].length !== 1) throw new ContractError(`${request.operation} requires a rank-1 vector`);
      if (shapes[0][0] < (spec.min_length ?? 0)) throw new ContractError(`${request.operation} vector is too short`);
      break;
    case "vector_binary_same_length":
      if (shapes[0].length !== 1 || !sameShape(shapes[0], shapes[1])) throw new ContractError(`${request.operation} requires equal-length rank-1 vectors`);
      if (shapes[0][0] < (spec.min_length ?? 0)) throw new ContractError(`${request.operation} vectors are too short`);
      break;
    case "matrix_multiply":
      if (shapes[0].length !== 2 || shapes[1].length !== 2) throw new ContractError("matmul requires two rank-2 matrices");
      if (shapes[0][1] !== shapes[1][0]) throw new ContractError(`matmul inner dimensions differ: ${JSON.stringify(shapes[0])} @ ${JSON.stringify(shapes[1])}`);
      if ([...shapes[0], ...shapes[1]].some((n) => n < 1)) throw new ContractError("matmul matrices must be non-empty");
      {
        const estimatedOps = shapes[0][0] * shapes[0][1] * shapes[1][1];
        const resultCount = shapes[0][0] * shapes[1][1];
        if (estimatedOps > RESOURCE_LIMITS.max_estimated_operations) throw new ContractError(`estimated operation count ${estimatedOps} exceeds contract limit ${RESOURCE_LIMITS.max_estimated_operations}`);
        if (resultCount > RESOURCE_LIMITS.max_result_scalar_count) throw new ContractError(`result scalar count ${resultCount} exceeds contract limit ${RESOURCE_LIMITS.max_result_scalar_count}`);
      }
      break;
    case "square_matrix_unary": {
      if (shapes[0].length !== 2 || shapes[0][0] !== shapes[0][1] || shapes[0][0] < 1) throw new ContractError(`${request.operation} requires a non-empty square matrix`);
      const n = shapes[0][0];
      if (n * n * n > RESOURCE_LIMITS.max_estimated_operations) throw new ContractError("estimated cubic matrix work exceeds contract limit");
      const resultCount = request.operation === "det" ? 1 : n * n;
      if (resultCount > RESOURCE_LIMITS.max_result_scalar_count) throw new ContractError("result scalar count exceeds contract limit");
      break;
    }
    case "linear_solve": {
      if (shapes[0].length !== 2 || shapes[0][0] !== shapes[0][1] || shapes[0][0] < 1) throw new ContractError("solve requires a non-empty square coefficient matrix");
      const n = shapes[0][0];
      let resultCount; let rhsCols = 1;
      if (shapes[1].length === 1) {
        if (shapes[1][0] !== n) throw new ContractError("solve right-hand vector length must match matrix dimension");
        resultCount = n;
      } else if (shapes[1].length === 2) {
        if (shapes[1][0] !== n || shapes[1][1] < 1) throw new ContractError("solve right-hand matrix row count must match coefficient matrix");
        rhsCols = shapes[1][1]; resultCount = n * rhsCols;
      } else throw new ContractError("solve right-hand operand must be a vector or matrix");
      if (n * n * Math.max(n, rhsCols) > RESOURCE_LIMITS.max_estimated_operations) throw new ContractError("estimated linear solve work exceeds contract limit");
      if (resultCount > RESOURCE_LIMITS.max_result_scalar_count) throw new ContractError("result scalar count exceeds contract limit");
      break;
    }
    default:
      throw new ContractError(`unknown contract signature: ${spec.signature}`);
  }

  for (const shape of shapes) {
    if (shape.length === 1 && shape[0] > RESOURCE_LIMITS.max_vector_length) throw new ContractError("vector length exceeds contract limit");
    if (shape.length === 2 && (shape[0] > RESOURCE_LIMITS.max_matrix_rows || shape[1] > RESOURCE_LIMITS.max_matrix_cols)) {
      throw new ContractError("matrix dimensions exceed contract limit");
    }
  }
  validateConstraints(request, spec.constraints ?? []);
  if (request.operation === "pow" && request.mode === "exact") {
    const exponent = request.operands[1];
    let integer = false;
    if (typeof exponent === "number") integer = Number.isInteger(exponent);
    else if (typeof exponent === "string") {
      if (/^[-+]?\d+$/.test(exponent)) integer = true;
      else if (/^[-+]?\d+\/[-+]?\d+$/.test(exponent)) {
        const [num, den] = exponent.split("/").map(Number);
        integer = den !== 0 && num % den === 0;
      }
    }
    if (!integer) throw new ContractError("exact pow exponent must be an integer");
    const q = Number(exponent);
    const magnitude = Number.isFinite(q) ? Math.abs(q) : (() => {
      if (typeof exponent === "string" && /^[-+]?\d+\/[-+]?\d+$/.test(exponent)) {
        const [num, den] = exponent.split("/").map(Number); return Math.abs(num / den);
      }
      return Infinity;
    })();
    if (magnitude > (RESOURCE_LIMITS.max_exact_power_exponent ?? 100000)) throw new ContractError("exact pow exponent exceeds resource limit");
  }
  if (request.operation === "pow" && request.mode === "interval") {
    const [lo, hi] = intervalBounds(request.operands[1]);
    if (lo !== hi || !Number.isInteger(lo)) throw new ContractError("interval pow exponent must be a degenerate integer interval");
    if (Math.abs(lo) > (RESOURCE_LIMITS.max_exact_power_exponent ?? 100000)) throw new ContractError("interval pow exponent exceeds resource limit");
  }
}

function validateConstraints(request, constraints) {
  const a = request.operands;
  for (const constraint of constraints) {
    if (constraint === "nonzero_operand_1") {
      if (request.mode === "interval") {
        const [lo, hi] = intervalBounds(a[1]);
        if (lo <= 0 && hi >= 0) throw new ContractError("interval denominator may not contain zero");
      } else if (asReal(a[1]) === 0) throw new ContractError("division by zero is prohibited");
    }
    if (constraint === "operand_0_nonnegative") {
      if (request.mode === "interval") { const [lo] = intervalBounds(a[0]); if (lo < 0) throw new ContractError("sqrt interval input must be nonnegative"); }
      else if (asReal(a[0]) < 0) throw new ContractError("sqrt real-domain input must be nonnegative");
    }
    if (constraint === "operand_0_positive") {
      if (request.mode === "interval") { const [lo] = intervalBounds(a[0]); if (lo <= 0) throw new ContractError("log interval input must be strictly positive"); }
      else if (asReal(a[0]) <= 0) throw new ContractError("log real-domain input must be positive");
    }
    if (constraint === "log_base_valid_if_present" && a.length === 2) {
      if (request.mode === "interval") {
        const [lo, hi] = intervalBounds(a[1]);
        if (lo <= 0 || (lo <= 1 && hi >= 1)) throw new ContractError("log interval base must be positive and must not contain 1");
      } else {
        const base = asReal(a[1]);
        if (base <= 0 || base === 1) throw new ContractError("log base must be positive and not equal to 1");
      }
    }
  }
}

function intervalBounds(value) {
  if (value && typeof value === "object" && !Array.isArray(value) && value.$type === "interval") {
    return [intervalEndpoint(value.lo), intervalEndpoint(value.hi)];
  }
  const x = intervalEndpoint(value);
  return [x, x];
}

function validateStringLengths(value, limit) {
  if (typeof value === "string") { if (value.length > limit) throw new ContractError(`numeric string length exceeds contract limit ${limit}`); return; }
  if (Array.isArray(value)) { for (const item of value) validateStringLengths(item, limit); return; }
  if (value && typeof value === "object") { for (const item of Object.values(value)) validateStringLengths(item, limit); }
}

function validateScalars(value, mode) {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    if (mode !== "interval" || value.$type !== "interval") throw new ContractError("object operands are reserved for interval mode");
    if (!("lo" in value) || !("hi" in value)) throw new ContractError("interval operand requires lo and hi endpoints");
    const lo = intervalEndpoint(value.lo);
    const hi = intervalEndpoint(value.hi);
    if (lo > hi) throw new ContractError("interval lower endpoint exceeds upper endpoint");
    return;
  }
  if (Array.isArray(value)) {
    for (const item of value) validateScalars(item, mode);
    return;
  }
  if (typeof value === "boolean") throw new ContractError("boolean values are not numeric operands");
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new ContractError("non-finite numeric input is prohibited");
    return;
  }
  if (typeof value === "string") {
    if (!["auto", "exact", "high_precision", "interval"].includes(mode)) throw new ContractError("numeric strings require auto, exact, high_precision, or interval mode");
    if (Number.isFinite(Number(value))) return;
    if (["auto", "exact", "interval"].includes(mode) && /^[-+]?\d+\/[-+]?\d+$/.test(value)) {
      const [num, den] = value.split("/").map(Number);
      if (Number.isFinite(num) && Number.isFinite(den) && den !== 0) return;
    }
    throw new ContractError(`invalid numeric string: ${JSON.stringify(value)}`);
  }
  throw new ContractError(`unsupported operand scalar type: ${typeof value}`);
}

function intervalEndpoint(value) {
  if (typeof value === "boolean") throw new ContractError("boolean interval endpoint is prohibited");
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new ContractError("non-finite interval endpoint is prohibited");
    return value;
  }
  if (typeof value === "string") {
    const n = Number(value);
    if (Number.isFinite(n)) return n;
    if (/^[-+]?\d+\/[-+]?\d+$/.test(value)) {
      const [num, den] = value.split("/").map(Number);
      if (den !== 0) return num / den;
    }
  }
  if (value && typeof value === "object" && value.$type === "fraction") {
    const num = Number(value.numerator), den = Number(value.denominator);
    if (Number.isFinite(num) && Number.isFinite(den) && den !== 0) return num / den;
  }
  throw new ContractError(`invalid interval endpoint: ${JSON.stringify(value)}`);
}

function shapeOf(value, depth = 0) {
  if (!Array.isArray(value)) return [];
  if (depth >= RESOURCE_LIMITS.max_rank) throw new ContractError("operand rank exceeds contract limit");
  if (value.length === 0) return [0];
  const first = shapeOf(value[0], depth + 1);
  for (let i = 1; i < value.length; i += 1) {
    const next = shapeOf(value[i], depth + 1);
    if (!sameShape(first, next)) throw new ContractError("ragged arrays are prohibited");
  }
  return [value.length, ...first];
}

function scalarCount(value) {
  let count = 0;
  const stack = [value];
  while (stack.length) {
    const item = stack.pop();
    if (Array.isArray(item)) { for (const child of item) stack.push(child); }
    else count += 1;
  }
  return count;
}

function sameShape(a, b) {
  return a.length === b.length && a.every((x, i) => x === b[i]);
}

function asReal(value) {
  let x = Number(value);
  if (!Number.isFinite(x) && typeof value === "string" && /^[-+]?\d+\/[-+]?\d+$/.test(value)) {
    const [num, den] = value.split("/").map(Number);
    x = den === 0 ? Number.NaN : num / den;
  }
  if (!Number.isFinite(x)) throw new ContractError(`operand is not a finite real value: ${JSON.stringify(value)}`);
  return x;
}
