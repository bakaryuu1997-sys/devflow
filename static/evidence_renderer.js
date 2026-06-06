function renderEvidence(markdown) {
  if (!markdown || !markdown.trim()) {
    return renderEmpty("No evidence report yet. Run the release gate first.");
  }
  const sections = parseEvidenceSections(markdown);
  const cards = sections.map(section => `
    <article class="evidence-card">
      <div class="evidence-card-head">
        <h4>${escapeHtml(section.title)}</h4>
        <span>${section.items.length} item(s)</span>
      </div>
      ${renderEvidenceItems(section.items)}
    </article>
  `).join("");
  return `
    <div class="evidence-toolbar">
      <div>
        <strong>Evidence Report Preview</strong>
        <p>Readable preview below. Markdown export is still preserved.</p>
      </div>
      <div class="evidence-actions">
        <button onclick="copyEvidenceMarkdown()">Copy Markdown</button>
        <a href="/api/projects/1/evidence.md?release_id=1">Download .md</a>
      </div>
    </div>
    <div class="evidence-grid">${cards}</div>
    ${debugBlock(markdown)}
  `;
}

function parseEvidenceSections(markdown) {
  const lines = markdown.split("\n");
  const sections = [];
  let current = { title: "Summary", items: [] };
  for (const line of lines) {
    if (line.startsWith("## ")) {
      sections.push(current);
      current = { title: line.replace(/^##\s+/, "").trim(), items: [] };
    } else if (line.startsWith("- ")) {
      current.items.push(line.replace(/^-\s+/, "").trim());
    } else if (line.trim() && !line.startsWith("#")) {
      current.items.push(line.trim());
    }
  }
  sections.push(current);
  return sections.filter(section => section.items.length > 0 || section.title !== "Summary");
}

function renderEvidenceItems(items) {
  if (!items || items.length === 0) {
    return '<p class="empty-inline">No items in this section.</p>';
  }
  return `<ul>${items.map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

async function copyEvidenceMarkdown() {
  if (!window.lastEvidenceMarkdown) return toast("No evidence markdown loaded yet.");
  await navigator.clipboard.writeText(window.lastEvidenceMarkdown);
  toast("Evidence markdown copied.");
}
