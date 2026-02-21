let currentReport = null;

const out = document.getElementById("out");
const btnPdf = document.getElementById("pdf");

function esc(s){ return String(s || "").replaceAll("<","&lt;").replaceAll(">","&gt;"); }

function render(report){
  currentReport = report;
  btnPdf.disabled = !report || report.error;

  if(report?.error){
    out.innerHTML = `<div class="err">${esc(report.error)}</div>`;
    return;
  }

  const pf = report.priority_fixes || {};
  const box = (p) => {
    const items = (pf[p] || []).slice(0, 30).map(x => `
      <li>
        <b>${esc(x.code || "")}</b> — ${esc(x.message || "")}
        ${x.url ? `<div class="muted">${esc(x.url)}</div>` : ""}
        ${x.fix ? `<div class="fix">Fix: ${esc(x.fix)}</div>` : ""}
      </li>
    `).join("");
    return `
      <div class="section">
        <h2>${p} Fixes <span class="pill">${(pf[p]||[]).length}</span></h2>
        <ul>${items || "<li>No issues found here 🎉</li>"}</ul>
      </div>
    `;
  };

  const pages = (report.pages || []).slice(0, 10).map(p => `
    <div class="page">
      <h3>${esc(p.url)}</h3>
      <div class="grid">
        <div><b>Title:</b> ${esc(p.title || "(missing)")}</div>
        <div><b>Meta desc:</b> ${esc(p.meta_description || "(missing)")}</div>
        <div><b>H1 count:</b> ${esc(p.headings?.h1 ?? 0)}</div>
        <div><b>Images missing alt:</b> ${esc(p.images_missing_alt ?? 0)} / ${esc(p.images_total ?? 0)}</div>
      </div>
      <div class="suggest">
        <div><b>Suggested title:</b> ${esc(p.suggestions?.suggested_title || "")}</div>
        <div><b>Suggested description:</b> ${esc(p.suggestions?.suggested_meta_description || "")}</div>
      </div>
    </div>
  `).join("");

  out.innerHTML = `
    <div class="meta">
      <div><b>Site:</b> ${esc(report.site?.url)}</div>
      <div><b>Pages crawled:</b> ${esc(report.site?.pages_crawled)}</div>
      <div><b>Target keyword:</b> ${esc(report.inputs?.target_keyword || "—")}</div>
    </div>
    ${box("P1")}
    ${box("P2")}
    ${box("P3")}
    <div class="section">
      <h2>Pages (top 10)</h2>
      ${pages}
    </div>
  `;
}

document.getElementById("run").onclick = async () => {
  const url = document.getElementById("url").value.trim();
  const kw = document.getElementById("kw").value.trim();
  out.innerHTML = `<div class="muted">Running audit…</div>`;
  const qs = new URLSearchParams({ url });
  if(kw) qs.set("target_keyword", kw);
  const res = await fetch(`http://localhost:8000/api/audit?${qs.toString()}`);
  render(await res.json());
};

document.getElementById("demo").onclick = () => {
  render({
    site: { url: "https://demo.local", host: "demo.local", pages_crawled: 3 },
    inputs: { target_keyword: "ai automation", max_pages: 25, max_depth: 2 },
    priority_fixes: {
      P1: [{priority:"P1",code:"MISSING_TITLE",message:"Missing <title> tag.",url:"/services",fix:"Add a unique title (50–60 chars) with primary keyword."}],
      P2: [],
      P3: []
    },
    pages: []
  });
};

btnPdf.onclick = async () => {
  const res = await fetch("http://localhost:8000/api/pdf", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ report: currentReport })
  });
  const blob = await res.blob();
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "seo-audit-report.pdf";
  a.click();
};