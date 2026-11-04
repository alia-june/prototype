const $ = (id) => document.getElementById(id);

const els = {
  form: $("computeForm"), operation: $("operation"), mode: $("mode"), operands: $("operands"),
  precision: $("precision"), tolerance: $("tolerance"), deterministic: $("deterministic"),
  allowWeb: $("allowWeb"), allowLlm: $("allowLlm"), runButton: $("runButton"),
  runtimeStatus: $("runtimeStatus"), contractVersion: $("contractVersion"), operationId: $("operationId"),
  signature: $("signature"), arity: $("arity"), statusBadge: $("statusBadge"), emptyState: $("emptyState"),
  resultContent: $("resultContent"), resultValue: $("resultValue"), backend: $("backend"),
  verified: $("verified"), authority: $("authority"), exact: $("exact"), trace: $("trace"),
  metadata: $("metadata"), rawResponse: $("rawResponse"), errorBox: $("errorBox"), loadExample: $("loadExample"), clearResult: $("clearResult"),
};

let contract = null;

const EXAMPLES = {
  add: [21, 21], sub: [100, 58], mul: [6, 7], div: [22, 7], pow: [2, 16],
  sqrt: [2], exp: [1], log: [8, 2], sin: [1.5707963267948966], cos: [0], tan: [0.7853981633974483],
  sum: [[1, 2, 3, 4, 5]], product: [[1, 2, 3, 4, 5]], mean: [[2, 4, 6, 8]],
  min: [[3, -4, 9, 0]], max: [[3, -4, 9, 0]], norm: [[3, 4]], dot: [[1, 2, 3], [4, 5, 6]],
  matmul: [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
};

function pretty(value) { return JSON.stringify(value, null, 2); }

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({ status: "failed", error: `HTTP ${response.status}` }));
  if (!response.ok && !body.status) body.status = "failed";
  return body;
}

async function initialize() {
  try {
    const [health, loadedContract] = await Promise.all([fetchJson("/api/health"), fetchJson("/api/contracts")]);
    contract = loadedContract;
    els.runtimeStatus.innerHTML = '<span class="dot good"></span> local service online';
    els.contractVersion.textContent = `contract ${contract.contract_version}`;
    const names = Object.keys(contract.operations);
    els.operation.replaceChildren(...names.map((name) => {
      const option = document.createElement("option"); option.value = name; option.textContent = name; return option;
    }));
    if (health.ui_version) els.runtimeStatus.title = `UI ${health.ui_version}; default web/LLM providers are not configured`;
    updateOperation();
  } catch (error) {
    els.runtimeStatus.innerHTML = '<span class="dot bad"></span> service unavailable';
    showBoundaryError(error);
  }
}

function updateOperation() {
  if (!contract) return;
  const name = els.operation.value;
  const spec = contract.operations[name];
  if (!spec) return;
  els.operationId.textContent = spec.operation_id;
  els.signature.textContent = spec.signature;
  els.arity.textContent = `arity ${spec.arity.join("/")}`;
  for (const option of els.mode.options) option.disabled = !spec.modes.includes(option.value);
  if (!spec.modes.includes(els.mode.value)) els.mode.value = spec.modes[0];
  loadExample();
}

function loadExample() {
  const example = EXAMPLES[els.operation.value] ?? [0];
  els.operands.value = pretty(example);
}

function buildRequest() {
  let operands;
  try { operands = JSON.parse(els.operands.value); }
  catch (error) { throw new Error(`Operands are not valid JSON: ${error.message}`); }
  if (!Array.isArray(operands)) throw new Error("Operands must be a JSON array whose items are operands.");
  const precision = els.precision.value.trim() === "" ? null : Number(els.precision.value);
  const tolerance = Number(els.tolerance.value);
  return {
    operation: els.operation.value,
    operands,
    mode: els.mode.value,
    precision,
    tolerance,
    deterministic: els.deterministic.value === "true",
    allow_web: els.allowWeb.checked,
    allow_llm: els.allowLlm.checked,
    metadata: { source: "javascript_frontend", ui_version: "0.5.0" },
  };
}

function badgeClass(status) {
  if (["verified", "computed", "externally_verified"].includes(status)) return "good";
  if (["web_sourced", "llm_inferred"].includes(status)) return "warn";
  if (status === "failed") return "bad";
  return "neutral";
}

function renderResult(result) {
  els.emptyState.classList.add("hidden");
  els.resultContent.classList.remove("hidden");
  els.statusBadge.textContent = result.status ?? "unknown";
  els.statusBadge.className = `badge ${badgeClass(result.status)}`;
  els.resultValue.textContent = pretty(result.value);
  if (result.error) { els.errorBox.textContent = result.error_code ? `${result.error_code}: ${result.error}` : result.error; els.errorBox.classList.remove("hidden"); }
  else { els.errorBox.textContent = ""; els.errorBox.classList.add("hidden"); }
  els.backend.textContent = result.backend ?? "—";
  els.verified.textContent = String(Boolean(result.verified));
  els.authority.textContent = result.authority ?? "—";
  els.exact.textContent = String(Boolean(result.exact));
  els.trace.replaceChildren(...(result.trace ?? []).map((step) => {
    const li = document.createElement("li"); li.textContent = step; return li;
  }));
  els.metadata.textContent = pretty(result.metadata ?? {});
  els.rawResponse.textContent = pretty(result);
}

function showBoundaryError(error) {
  renderResult({ value: null, status: "failed", backend: "javascript_frontend", verified: false, exact: false,
    authority: "none", error: error.message, trace: ["browser front-end boundary failure"], metadata: {} });
}

els.operation.addEventListener("change", updateOperation);
els.loadExample.addEventListener("click", loadExample);
els.clearResult.addEventListener("click", () => {
  els.resultContent.classList.add("hidden"); els.emptyState.classList.remove("hidden");
  els.statusBadge.textContent = "idle"; els.statusBadge.className = "badge neutral";
});
els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  els.runButton.disabled = true; els.runButton.textContent = "Computing…";
  try {
    const request = buildRequest();
    const result = await fetchJson("/api/compute", {
      method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(request),
    });
    renderResult(result);
  } catch (error) { showBoundaryError(error); }
  finally { els.runButton.disabled = false; els.runButton.textContent = "Compute"; }
});

initialize();
