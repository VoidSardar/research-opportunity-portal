const API_URL = "http://127.0.0.1:8000/api/opportunities";

const formModal = new bootstrap.Modal(document.getElementById("formModal"));
const detailsModal = new bootstrap.Modal(
  document.getElementById("detailsModal"),
);
const form = document.getElementById("oppForm");
const FIELDS = [
  "title",
  "description",
  "research_area",
  "faculty_name",
  "department",
  "required_skills",
  "available_positions",
  "application_deadline",
  "status",
];

// ---------- helpers ----------

function esc(text) {
  const d = document.createElement("div");
  d.textContent = text;
  return d.innerHTML;
}

function showMessage(type, text) {
  document.getElementById("message").innerHTML =
    `<div class="alert alert-${type} alert-dismissible fade show">
       ${esc(text)}
       <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
     </div>`;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// One place for all API calls; turns error responses into readable messages
async function api(url, options = {}) {
  let res;
  try {
    res = await fetch(url, options);
  } catch (e) {
    throw new Error("Cannot reach the server. Is the backend running?");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    let msg = data.detail || "Something went wrong";
    if (data.errors) msg += ": " + data.errors.join("; ");
    throw new Error(`${msg} (HTTP ${res.status})`);
  }
  return data;
}

// ---------- list ----------

async function loadOpportunities() {
  try {
    const list = await api(API_URL);
    const body = document.getElementById("tableBody");
    if (list.length === 0) {
      body.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-4">
        No research opportunities yet. Click "New Opportunity" to add one.</td></tr>`;
      return;
    }
    body.innerHTML = list
      .map(
        (o) => `
      <tr>
        <td>${o.id}</td>
        <td>${esc(o.title)}</td>
        <td>${esc(o.faculty_name)}</td>
        <td>${esc(o.research_area)}</td>
        <td>${o.available_positions}</td>
        <td>${esc(o.application_deadline)}</td>
        <td><span class="badge bg-${o.status === "Open" ? "success" : "secondary"}">${o.status}</span></td>
        <td class="text-end text-nowrap">
          <button class="btn btn-sm btn-outline-primary" onclick="viewDetails(${o.id})">View</button>
          <button class="btn btn-sm btn-outline-secondary" onclick="openEdit(${o.id})">Edit</button>
          ${
            o.status === "Open"
              ? `<button class="btn btn-sm btn-outline-warning" onclick="closeOpportunity(${o.id})">Close</button>`
              : ""
          }
          <button class="btn btn-sm btn-outline-danger" onclick="deleteOpportunity(${o.id})">Delete</button>
        </td>
      </tr>`,
      )
      .join("");
  } catch (e) {
    showMessage("danger", e.message);
  }
}

// ---------- details ----------

async function viewDetails(id) {
  try {
    const o = await api(`${API_URL}/${id}`);
    document.getElementById("detailsBody").innerHTML = `
      <h5>${esc(o.title)}
        <span class="badge bg-${o.status === "Open" ? "success" : "secondary"}">${o.status}</span></h5>
      <p class="text-muted">${esc(o.description)}</p>
      <dl class="row mb-0">
        <dt class="col-sm-4">ID</dt><dd class="col-sm-8">${o.id}</dd>
        <dt class="col-sm-4">Research Area</dt><dd class="col-sm-8">${esc(o.research_area)}</dd>
        <dt class="col-sm-4">Faculty Member</dt><dd class="col-sm-8">${esc(o.faculty_name)}</dd>
        <dt class="col-sm-4">Department</dt><dd class="col-sm-8">${esc(o.department)}</dd>
        <dt class="col-sm-4">Required Skills</dt><dd class="col-sm-8">${esc(o.required_skills)}</dd>
        <dt class="col-sm-4">Available Positions</dt><dd class="col-sm-8">${o.available_positions}</dd>
        <dt class="col-sm-4">Application Deadline</dt><dd class="col-sm-8">${esc(o.application_deadline)}</dd>
      </dl>`;
    detailsModal.show();
  } catch (e) {
    showMessage("danger", e.message);
    loadOpportunities();
  }
}

// ---------- create / edit ----------

function resetForm() {
  form.reset();
  form.classList.remove("was-validated");
  document.getElementById("oppId").value = "";
}

function openCreate() {
  resetForm();
  document.getElementById("formTitle").textContent = "New Opportunity";
  formModal.show();
}

async function openEdit(id) {
  try {
    const o = await api(`${API_URL}/${id}`);
    resetForm();
    document.getElementById("formTitle").textContent =
      `Edit Opportunity #${id}`;
    document.getElementById("oppId").value = id;
    FIELDS.forEach((f) => (document.getElementById(f).value = o[f]));
    formModal.show();
  } catch (e) {
    showMessage("danger", e.message);
    loadOpportunities();
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  // basic frontend validation
  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    return;
  }

  const payload = {};
  FIELDS.forEach((f) => (payload[f] = document.getElementById(f).value.trim()));
  payload.available_positions = parseInt(payload.available_positions, 10);

  const id = document.getElementById("oppId").value;
  const isEdit = id !== "";

  try {
    await api(isEdit ? `${API_URL}/${id}` : API_URL, {
      method: isEdit ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    formModal.hide();
    showMessage(
      "success",
      isEdit
        ? "Opportunity updated successfully."
        : "Opportunity created successfully.",
    );
    loadOpportunities();
  } catch (e) {
    showMessage("danger", e.message);
  }
});

// ---------- close / delete ----------

async function closeOpportunity(id) {
  try {
    await api(`${API_URL}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "Closed" }),
    });
    showMessage("success", `Opportunity #${id} has been closed.`);
    loadOpportunities();
  } catch (e) {
    showMessage("danger", e.message);
  }
}

async function deleteOpportunity(id) {
  if (!confirm(`Delete opportunity #${id}? This cannot be undone.`)) return;
  try {
    await api(`${API_URL}/${id}`, { method: "DELETE" });
    showMessage("success", `Opportunity #${id} deleted successfully.`);
    loadOpportunities();
  } catch (e) {
    showMessage("danger", e.message);
    loadOpportunities();
  }
}

// load data from the API when the page opens
loadOpportunities();
