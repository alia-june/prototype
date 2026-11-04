(async function runReferenceOccurrenceInspector() {
  "use strict";

  const packet = globalThis.REFERENCE_OCCURRENCE_INSPECTOR_DATA;
  const core = globalThis.ReferenceInspectorCore;
  const state = {
    mode: "view:V0",
    selectedId: "occurrence:O0",
    family: "all",
    analysis: null
  };

  const $ = id => document.getElementById(id);
  const element = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text);
    return node;
  };
  const setPressed = (buttons, selected) => buttons.forEach(button => button.setAttribute("aria-pressed", String(button === selected)));
  const displayValue = value => typeof value === "string" ? value : JSON.stringify(value);

  function updateMetrics() {
    const fixture = packet.fixture;
    for (const [id, collection] of [
      ["metric-targets", "targets"],
      ["metric-relationships", "relationships"],
      ["metric-metadata", "metadata"],
      ["metric-occurrences", "occurrences"],
      ["metric-views", "views"]
    ]) $(id).textContent = Array.isArray(fixture[collection]) ? fixture[collection].length : "—";
    $("metric-findings").textContent = state.analysis.findings.length;
  }

  function updateStatus() {
    const card = $("overall-status");
    card.className = `status-card ${state.analysis.status}`;
    if (state.analysis.status === "valid") {
      $("status-title").textContent = "Snapshot verified";
      $("status-detail").textContent = "References, transformation and 3 payload digests pass";
    } else if (state.analysis.status === "partial") {
      $("status-title").textContent = "Structure valid";
      $("status-detail").textContent = "Browser digest verification is unavailable";
    } else {
      $("status-title").textContent = "Snapshot has findings";
      $("status-detail").textContent = `${state.analysis.findings.length} bounded finding${state.analysis.findings.length === 1 ? "" : "s"}`;
    }
  }

  function renderSourceDialog() {
    const container = $("source-identities");
    container.replaceChildren();
    packet.source_files.forEach(source => {
      const card = element("article", "source-record");
      card.append(
        element("strong", "", `${source.role}: ${source.path}`),
        element("code", "", `${source.bytes} bytes`),
        element("code", "", `sha256 ${source.sha256}`)
      );
      container.append(card);
    });
  }

  function selectRecord(id) {
    if (!state.analysis.byId.has(id)) return;
    state.selectedId = id;
    renderRecordIndex();
    renderSequence();
    renderDetail();
  }

  function renderRecordIndex() {
    const records = core.orderedRecords(packet.fixture).filter(record => state.family === "all" || record.kind === state.family);
    $("record-count").textContent = records.length;
    const container = $("record-list");
    container.replaceChildren();
    records.forEach(record => {
      const button = element("button", "record-row");
      button.type = "button";
      button.dataset.recordId = record.id;
      button.setAttribute("aria-pressed", String(record.id === state.selectedId));
      button.append(
        element("span", "row-kind", record.kind),
        element("strong", "", record.id),
        element("small", "", core.recordSummary(record))
      );
      button.addEventListener("click", () => selectRecord(record.id));
      container.append(button);
    });
  }

  function occurrenceCard(entry) {
    const wrapper = element("div", "occurrence-step");
    wrapper.append(element("span", "step-index", entry.position));
    const card = element("button", `occurrence-card${entry.occurrenceId === state.selectedId ? " selected" : ""}`);
    card.type = "button";
    card.dataset.recordId = entry.occurrenceId;
    const head = element("div", "occurrence-head");
    head.append(
      element("strong", "", entry.occurrenceId),
      element("span", `role-badge ${entry.target?.role || "unresolved"}`, entry.target?.role || "unresolved")
    );
    const references = element("div", "occurrence-refs");
    if (entry.occurrence) {
      references.append(
        element("span", "ref-chip", `target ${entry.occurrence.target_ref}`),
        element("span", "ref-chip", `relation ${entry.occurrence.relationship_ref}`),
        element("span", "ref-chip", `metadata ${entry.occurrence.metadata_ref}`)
      );
    }
    card.append(head, element("p", "occurrence-preview", core.targetPreview(entry.target)), references);
    card.addEventListener("click", () => selectRecord(entry.occurrenceId));
    wrapper.append(card);
    return wrapper;
  }

  function renderSingleView(viewId) {
    const resolved = core.resolveView(packet.fixture, viewId, state.analysis);
    const content = $("sequence-content");
    content.replaceChildren();
    if (!resolved) {
      content.append(element("p", "detail-summary", `Unable to resolve ${viewId}.`));
      return;
    }
    const chronological = viewId === "view:V0";
    $("sequence-title").textContent = chronological ? "Chronological inspection" : "Reverse inspection";
    $("sequence-chip").textContent = chronological ? "V0" : "V1";
    $("view-explanation").textContent = chronological
      ? "Source → transformation → result. Array position supplies order in this view only."
      : "Result → transformation → source. Traversal reverses; the relationship and history do not.";
    const rail = element("div", "sequence-rail");
    resolved.entries.forEach(entry => rail.append(occurrenceCard(entry)));
    content.append(rail);
  }

  function compareColumn(resolved, label) {
    const column = element("article", "compare-column");
    column.append(element("h3", "", label), element("p", "", resolved.view.id));
    resolved.entries.forEach(entry => {
      const row = element("button", "compare-item");
      row.type = "button";
      const identityIndex = ["occurrence:O0", "occurrence:O1", "occurrence:O2"].indexOf(entry.occurrenceId);
      row.append(
        element("span", `identity-mark identity-${Math.max(0, identityIndex)}`),
        element("span", "", `${entry.position}  ${entry.occurrenceId}  ${core.targetPreview(entry.target)}`)
      );
      row.addEventListener("click", () => selectRecord(entry.occurrenceId));
      column.append(row);
    });
    return column;
  }

  function renderComparison() {
    const comparison = core.compareViews(packet.fixture, "view:V0", "view:V1");
    const content = $("sequence-content");
    content.replaceChildren();
    $("sequence-title").textContent = "Same occurrences, different order";
    $("sequence-chip").textContent = "V0 : V1";
    $("view-explanation").textContent = "Identity is stable across the two views. Matching colors mark the same occurrence; no record is rewritten.";
    if (!comparison) {
      content.append(element("p", "detail-summary", "Unable to compare the required views."));
      return;
    }
    const grid = element("div", "compare-grid");
    grid.append(compareColumn(comparison.left, "Chronological"), compareColumn(comparison.right, "Reverse inspection"));
    const facts = element("div", "compare-facts");
    for (const [label, value] of [
      ["Occurrence set", comparison.sameOccurrenceSet ? "Identical" : "Different"],
      ["Order", comparison.sameOrder ? "Identical" : "Different"],
      ["History mutation", comparison.historyMutated ? "Yes" : "None"]
    ]) {
      const fact = element("div");
      fact.append(element("small", "", label), element("strong", "", value));
      facts.append(fact);
    }
    grid.append(facts);
    content.append(grid);
  }

  function renderSequence() {
    if (state.mode === "compare") renderComparison();
    else renderSingleView(state.mode);
  }

  function renderDetail() {
    const record = state.analysis.byId.get(state.selectedId);
    const title = $("detail-title");
    const kind = $("detail-kind");
    const summary = $("detail-summary");
    const fields = $("detail-fields");
    const links = $("reference-links");
    const digest = $("digest-status");
    fields.replaceChildren();
    links.replaceChildren();
    digest.hidden = true;
    digest.className = "digest-status";
    if (!record) {
      title.textContent = "Unresolved selection";
      kind.textContent = "—";
      kind.className = "kind-chip neutral";
      summary.textContent = "The selected identifier did not resolve to a record.";
      return;
    }
    title.textContent = record.id;
    kind.textContent = record.kind;
    kind.className = `kind-chip ${record.kind}`;
    summary.textContent = core.recordSummary(record);
    for (const [field, value] of Object.entries(record)) {
      const dt = element("dt", "", field);
      const dd = element("dd", "", displayValue(value));
      fields.append(dt, dd);
    }
    if (record.kind === "target") {
      const result = state.analysis.digestResults.get(record.id);
      if (result) {
        digest.hidden = false;
        digest.classList.add(result.status);
        digest.textContent = result.status === "verified"
          ? `SHA-256 verified · ${result.actual}`
          : result.status === "mismatch"
            ? `SHA-256 mismatch · expected ${result.expected} · actual ${result.actual || "unavailable"}`
            : `SHA-256 verification unavailable · expected ${result.expected}`;
      }
    }
    const references = core.referenceIds(record);
    if (references.length) {
      links.append(element("p", "", "Follow references"));
      references.forEach(reference => {
        const button = element("button", "reference-button", reference);
        button.type = "button";
        button.disabled = !state.analysis.byId.has(reference);
        button.addEventListener("click", () => selectRecord(reference));
        links.append(button);
      });
    }
  }

  function renderFindings() {
    const count = state.analysis.findings.length;
    $("validation-summary").textContent = count ? `${count} finding${count === 1 ? "" : "s"}` : "No findings";
    const content = $("validation-content");
    content.replaceChildren();
    if (!count) {
      content.append(element("p", "clean-message", "The resolved display packet passes the inspector's structural, reference, transformation and digest checks."));
      return;
    }
    content.append(element("p", "", "Findings are displayed without modifying or repairing the snapshot."));
    const list = element("ul", "finding-list");
    state.analysis.findings.forEach(finding => list.append(element("li", "", `${finding.code} · ${finding.path} · ${finding.message}`)));
    content.append(list);
  }

  function bindControls() {
    const modeButtons = [...document.querySelectorAll("[data-mode]")];
    modeButtons.forEach(button => button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      setPressed(modeButtons, button);
      renderSequence();
    }));
    const familyButtons = [...document.querySelectorAll("[data-family]")];
    familyButtons.forEach(button => button.addEventListener("click", () => {
      state.family = button.dataset.family;
      setPressed(familyButtons, button);
      renderRecordIndex();
    }));
    document.querySelectorAll("[data-record-id]").forEach(button => button.addEventListener("click", () => selectRecord(button.dataset.recordId)));
    const dialog = $("source-dialog");
    $("show-source").addEventListener("click", () => dialog.showModal());
  }

  try {
    if (!packet || !core) throw new Error("Inspector data or core module is unavailable.");
    state.analysis = await core.analyzePacket(packet);
    renderSourceDialog();
    updateMetrics();
    updateStatus();
    bindControls();
    renderRecordIndex();
    renderSequence();
    renderDetail();
    renderFindings();
  } catch (error) {
    const card = $("overall-status");
    card.className = "status-card invalid";
    $("status-title").textContent = "Inspector failed to initialize";
    $("status-detail").textContent = error && error.message ? error.message : String(error);
    $("metric-findings").textContent = "!";
  }
})();
