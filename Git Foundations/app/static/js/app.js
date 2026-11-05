"use strict";

const money = (n) => "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 2 });
const $ = (sel) => document.querySelector(sel);

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const data = res.status === 204 ? null : await res.json();
  if (!res.ok) throw new Error((data && data.error) || "Something went wrong.");
  return data;
}

function toast(message, isError = false) {
  const t = $("#toast");
  t.textContent = message;
  t.className = "show" + (isError ? " error" : "");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => (t.className = ""), 3000);
}

// Build elements with textContent only, so user input is never parsed as HTML.
function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  Object.assign(node, props);
  children.forEach((c) => node.append(c));
  return node;
}

// ---- Navigation -------------------------------------------------------------
function showView() {
  const name = location.hash.slice(1) || "overview";
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("active", v.id === name));
  document.querySelectorAll(".side a").forEach((a) => a.classList.toggle("active", a.dataset.view === name));
}

// ---- Data loaders -----------------------------------------------------------
async function loadStats() {
  const s = await api("/api/stats");
  $("#s-members").textContent = s.members;
  $("#s-pending").textContent = s.claims_pending;
  $("#s-approved").textContent = s.claims_approved;
  $("#s-total").textContent = money(s.approved_total);
}

async function loadPlans() {
  const plans = await api("/api/plans");
  const list = $("#plan-list");
  list.replaceChildren(...plans.map((p) => {
    const card = el("article", { className: "plan" }, el("h3", { textContent: p.name }),
      el("p", { textContent: p.description }));
    card.dataset.tier = p.tier;
    const dl = el("dl");
    [["From", money(p.base_premium) + " / month"], ["Deductible", money(p.deductible)],
     ["Coverage limit", money(p.coverage_limit)]].forEach(([k, v]) =>
      dl.append(el("dt", { textContent: k }), el("dd", { textContent: v })));
    card.append(dl);
    return card;
  }));
  document.querySelectorAll(".plan-select").forEach((sel) =>
    sel.replaceChildren(...plans.map((p) => el("option", { value: p.id, textContent: `${p.name} (${p.tier})` }))));
}

async function loadMembers() {
  const members = await api("/api/members");
  $("#member-empty").hidden = members.length > 0;
  $("#member-rows").replaceChildren(...members.map((m) => {
    const del = el("button", { className: "ghost", textContent: "Remove", type: "button" });
    del.addEventListener("click", async () => {
      if (!confirm(`Remove ${m.name} and their claims?`)) return;
      await run(async () => { await api(`/api/members/${m.id}`, { method: "DELETE" }); toast("Member removed."); });
    });

    // NEW: a plan dropdown for this member (5 lines)
    const planSel = $(".plan-select").cloneNode(true);
    planSel.value = m.plan_id;
    planSel.addEventListener("change", () => run(async () => {
      await api(`/api/members/${m.id}`, { method: "PATCH", body: { plan_id: planSel.value } });
      toast("Plan updated.");
    }));

    return el("tr", {}, el("td", { textContent: m.name }), el("td", { textContent: m.email }),
      // CHANGED: was el("td", { textContent: m.plan_name })
      el("td", {}, planSel), el("td", {}, del));
  }));
  $("#claim-member").replaceChildren(...members.map((m) => el("option", { value: m.id, textContent: m.name })));
}

async function loadClaims() {
  const claims = await api("/api/claims");
  $("#claim-empty").hidden = claims.length > 0;
  $("#claim-rows").replaceChildren(...claims.map((c) => {
    const actions = el("div", { className: "review" });
    if (c.status === "pending") {
      [["approved", "Approve"], ["rejected", "Reject"]].forEach(([status, label]) => {
        const b = el("button", { textContent: label, type: "button" });
        b.addEventListener("click", () => run(async () => {
          await api(`/api/claims/${c.id}`, { method: "PATCH", body: { status } });
          toast(`Claim ${status}.`);
        }));
        actions.append(b);
      });
    }
    return el("tr", {}, el("td", { textContent: c.member_name }), el("td", { textContent: c.description }),
      el("td", { textContent: money(c.amount) }),
      el("td", {}, el("span", { className: "badge " + c.status, textContent: c.status })),
      el("td", {}, actions));
  }));
}

const refresh = () => Promise.all([loadStats(), loadMembers(), loadClaims()]);

async function run(action) {
  try { await action(); await refresh(); }
  catch (err) { toast(err.message, true); }
}

// ---- Forms ------------------------------------------------------------------
const formData = (form) => Object.fromEntries(new FormData(form));

$("#quote-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const d = formData(e.target);
  try {
    const q = await api("/api/quote", { method: "POST", body: { ...d, smoker: !!d.smoker } });
    $("#quote-result").textContent = `${q.plan}: ${money(q.monthly_premium)} a month (${money(q.annual_premium)} a year)`;
  } catch (err) { $("#quote-result").textContent = ""; toast(err.message, true); }
});

$("#member-form").addEventListener("submit", (e) => {
  e.preventDefault();
  run(async () => {
    await api("/api/members", { method: "POST", body: formData(e.target) });
    e.target.reset(); toast("Member added.");
  });
});

$("#claim-form").addEventListener("submit", (e) => {
  e.preventDefault();
  run(async () => {
    await api("/api/claims", { method: "POST", body: formData(e.target) });
    e.target.reset(); toast("Claim filed.");
  });
});

window.addEventListener("hashchange", showView);
showView();
loadPlans().then(refresh).catch((err) => toast(err.message, true));
