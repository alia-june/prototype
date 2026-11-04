(() => {
  "use strict";
  const packet = window.AUTH18B_DATA;
  const records = Array.isArray(packet?.records) ? packet.records : [];
  const byId = new Map(records.map(record => [record.id, record]));
  const search = document.getElementById("search");
  const catalog = document.getElementById("catalog");
  const status = document.getElementById("status");
  const list = document.getElementById("record-list");
  let selectedId = "";

  const text = (value) => value == null ? "" : typeof value === "string" ? value : JSON.stringify(value);
  const recordStatus = record => record.status || record.mapping_status || record.access_status || "UNSPECIFIED";
  const recordTitle = record => record.term || record.title || record.id;
  const appendOption = (select, value) => { const option = document.createElement("option"); option.value = value; option.textContent = value; select.append(option); };
  [...new Set(records.map(r => r.catalog))].sort().forEach(value => appendOption(catalog, value));
  [...new Set(records.map(recordStatus))].sort().forEach(value => appendOption(status, value));

  document.getElementById("study-status").textContent = String(packet?.study_status || "UNAVAILABLE").replaceAll("_", " ");
  document.getElementById("metric-records").textContent = records.length;
  document.getElementById("metric-sources").textContent = records.filter(r => r.catalog === "sources").length;
  document.getElementById("metric-relations").textContent = records.filter(r => ["wordnet_relations", "generic_relations", "theory"].includes(r.catalog)).length;
  document.getElementById("metric-crosswalk").textContent = records.filter(r => r.catalog === "crosswalk").length;

  function showDetail(record) {
    selectedId = record.id;
    document.getElementById("detail-title").textContent = recordTitle(record);
    document.getElementById("detail-summary").textContent = record.summary || record.rationale || "No summary field.";
    const fields = document.getElementById("detail-fields");
    fields.replaceChildren();
    Object.entries(record).filter(([key]) => !["summary", "rationale", "links"].includes(key)).forEach(([key, value]) => {
      const dt = document.createElement("dt"); dt.textContent = key;
      const dd = document.createElement("dd"); dd.textContent = text(value);
      fields.append(dt, dd);
    });
    const linkPanel = document.getElementById("detail-links");
    linkPanel.replaceChildren();
    const targets = new Set([...(record.links || []), record.source_id, record.wordnet_id, record.theory_id, record.generic_relation_id].filter(Boolean));
    if (targets.size) {
      const label = document.createElement("p"); label.textContent = "Outgoing references"; linkPanel.append(label);
      targets.forEach(id => {
        const button = document.createElement("button"); button.type = "button"; button.textContent = id;
        button.addEventListener("click", () => { const target = byId.get(id); if (target) { showDetail(target); render(); } });
        linkPanel.append(button);
      });
    }
  }

  function render() {
    const needle = search.value.trim().toLowerCase();
    const visible = records.filter(record => (!catalog.value || record.catalog === catalog.value) &&
      (!status.value || recordStatus(record) === status.value) &&
      (!needle || JSON.stringify(record).toLowerCase().includes(needle)));
    document.getElementById("result-count").textContent = `${visible.length} shown`;
    list.replaceChildren();
    visible.forEach(record => {
      const button = document.createElement("button"); button.type = "button"; button.className = "record";
      button.setAttribute("aria-pressed", String(record.id === selectedId));
      const tag = document.createElement("span"); tag.className = "tag"; tag.textContent = record.catalog;
      const title = document.createElement("strong"); title.textContent = recordTitle(record);
      const meta = document.createElement("small"); meta.textContent = `${record.id} • ${recordStatus(record)}`;
      button.append(tag, title, meta);
      button.addEventListener("click", () => { showDetail(record); render(); });
      list.append(button);
    });
  }
  [search, catalog, status].forEach(control => control.addEventListener("input", render));
  document.getElementById("reset").addEventListener("click", () => { search.value = ""; catalog.value = ""; status.value = ""; render(); });
  render();
})();
