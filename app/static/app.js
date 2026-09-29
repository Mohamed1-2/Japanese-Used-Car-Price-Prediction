const state = { options: null, modelInfo: null };

const $ = (selector) => document.querySelector(selector);
const form = $("#valuation-form");
const manufacturer = $("#manufacturer");
const model = $("#model");
const mileageInput = form.elements.mileage_km;
const mileageRange = $("#mileage-range");

function option(value, label = value) {
  const item = document.createElement("option");
  item.value = value;
  item.textContent = label;
  return item;
}

function populateSelect(id, values) {
  const select = $(id);
  values.forEach((value) => select.append(option(value)));
}

function buildYears(referenceYear = new Date().getFullYear()) {
  const yearSelect = $("#registration-year");
  for (let year = referenceYear; year >= 1980; year -= 1) {
    yearSelect.append(option(String(year), String(year)));
  }
  yearSelect.value = String(Math.min(2021, referenceYear));
}

function updateModels() {
  const models = state.options?.manufacturer_to_models?.[manufacturer.value] || [];
  model.replaceChildren(option("", models.length ? "Select model" : "No models available"));
  models.forEach((name) => model.append(option(name)));
  model.disabled = models.length === 0;
}

async function loadApplicationData() {
  const status = $("#api-status");
  try {
    const [healthResponse, optionsResponse, infoResponse] = await Promise.all([
      fetch("/health"), fetch("/v1/options"), fetch("/v1/model-info")
    ]);
    if (!healthResponse.ok || !optionsResponse.ok || !infoResponse.ok) throw new Error("Service metadata unavailable");
    const health = await healthResponse.json();
    state.options = await optionsResponse.json();
    state.modelInfo = await infoResponse.json();

    Object.keys(state.options.manufacturer_to_models).sort((a, b) => a.localeCompare(b, "ja"))
      .forEach((name) => manufacturer.append(option(name)));
    populateSelect("#fuel", state.options.fuel_values || []);
    populateSelect("#transmission", state.options.transmission_values || []);
    populateSelect("#drivetrain", state.options.drivetrain_values || []);
    populateSelect("#prefecture", state.options.prefecture_values || []);
    buildYears(state.modelInfo.model_reference_year);
    $("#reference-year").textContent = state.modelInfo.model_reference_year;
    status.classList.toggle("ready", health.status === "ok");
    status.lastChild.textContent = health.status === "ok" ? " Model online" : " Model loading";
  } catch (error) {
    buildYears();
    status.lastChild.textContent = " Service unavailable";
    showError("Vehicle options could not be loaded. Refresh the page and try again.");
  }
}

function setPanel(panel) {
  ["#result-empty", "#result-loading", "#result-content", "#result-error"]
    .forEach((id) => { $(id).hidden = id !== panel; });
}

function showError(message) {
  $("#error-message").textContent = message;
  setPanel("#result-error");
}

function formatYen(value) {
  return new Intl.NumberFormat("ja-JP", { style: "currency", currency: "JPY", maximumFractionDigits: 0 }).format(value);
}

function payloadFromForm() {
  const data = new FormData(form);
  const payload = {};
  for (const [key, rawValue] of data.entries()) {
    const value = typeof rawValue === "string" ? rawValue.trim() : rawValue;
    if (value === "") continue;
    payload[key] = value;
  }
  payload.registration_year = Number(payload.registration_year);
  payload.mileage_km = Number(payload.mileage_km);
  if (payload.repair_history !== undefined) payload.repair_history = payload.repair_history === "true";
  return payload;
}

function renderResult(result, payload) {
  $("#fair-price").textContent = formatYen(result.estimated_fair_price_jpy);
  $("#range-low").textContent = formatYen(result.expected_range_low_jpy);
  $("#range-high").textContent = formatYen(result.expected_range_high_jpy);
  const span = Math.max(1, result.expected_range_high_jpy - result.expected_range_low_jpy);
  const position = Math.min(90, Math.max(10, ((result.estimated_fair_price_jpy - result.expected_range_low_jpy) / span) * 100));
  $("#range-marker").style.left = `${position}%`;
  const summary = [payload.manufacturer, payload.model, `${payload.registration_year}`, `${Number(payload.mileage_km).toLocaleString()} km`, payload.fuel].filter(Boolean);
  $("#vehicle-summary").replaceChildren(...summary.map((text) => { const chip = document.createElement("span"); chip.textContent = text; return chip; }));
  setPanel("#result-content");
}

async function fetchPrediction(payload) {
  const response = await fetch("/v1/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body?.error?.message || "The valuation request could not be completed.");
  return body;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const button = $("#submit-button");
  button.disabled = true;
  button.querySelector("span").textContent = "Calculating…";
  setPanel("#result-loading");
  $("#result-panel").scrollIntoView({ behavior: "smooth", block: "center" });
  try {
    const payload = payloadFromForm();
    renderResult(await fetchPrediction(payload), payload);
  } catch (error) {
    showError(error.message);
  } finally {
    button.disabled = false;
    button.querySelector("span").textContent = "Calculate fair value";
  }
});

manufacturer.addEventListener("change", updateModels);
mileageRange.addEventListener("input", () => { mileageInput.value = mileageRange.value; });
mileageInput.addEventListener("input", () => { mileageRange.value = Math.min(250000, Number(mileageInput.value || 0)); });
$("#reset-button").addEventListener("click", () => { form.reset(); model.disabled = true; updateModels(); mileageRange.value = mileageInput.value; setPanel("#result-empty"); form.scrollIntoView({ behavior: "smooth" }); });
$("#retry-button").addEventListener("click", () => { setPanel("#result-empty"); form.scrollIntoView({ behavior: "smooth" }); });

loadApplicationData();
