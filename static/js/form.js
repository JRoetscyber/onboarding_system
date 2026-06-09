const steps = Array.from(document.querySelectorAll(".form-step"));
const form = document.getElementById("onboardingForm");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const submitBtn = document.getElementById("submitBtn");
const spinner = document.getElementById("submitSpinner");
const progressBar = document.getElementById("progressBar");
const progressText = document.getElementById("progressText");
const stepLabel = document.getElementById("stepLabel");
let currentStep = 0;

function showStep(index) {
  steps.forEach((step, stepIndex) => step.classList.toggle("active", stepIndex === index));
  prevBtn.disabled = index === 0;
  nextBtn.classList.toggle("d-none", index === steps.length - 1);
  submitBtn.classList.toggle("d-none", index !== steps.length - 1);
  progressBar.style.width = `${Math.round(((index + 1) / steps.length) * 100)}%`;
  stepLabel.textContent = `Step ${index + 1} of ${steps.length}`;
  progressText.textContent = steps[index].dataset.title;
}

function validateStep() {
  const fields = Array.from(steps[currentStep].querySelectorAll("input, select, textarea"));
  let valid = true;
  fields.forEach((field) => {
    if (!field.checkValidity()) {
      field.classList.add("is-invalid");
      valid = false;
    } else {
      field.classList.remove("is-invalid");
    }
  });
  return valid;
}

nextBtn.addEventListener("click", () => {
  if (!validateStep()) return;
  currentStep = Math.min(currentStep + 1, steps.length - 1);
  showStep(currentStep);
  window.scrollTo({ top: 0, behavior: "smooth" });
});

prevBtn.addEventListener("click", () => {
  currentStep = Math.max(currentStep - 1, 0);
  showStep(currentStep);
});

form.addEventListener("input", (event) => {
  if (event.target.matches("[name='contact_name']")) {
    const target = form.querySelector("[name='main_contact_name']");
    if (target && !target.value) target.value = event.target.value;
  }
  if (event.target.matches("[name='contact_email']")) {
    const target = form.querySelector("[name='main_contact_email']");
    if (target && !target.value) target.value = event.target.value;
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!validateStep()) return;
  submitBtn.disabled = true;
  spinner.classList.remove("d-none");
  const response = await fetch("/api/onboard/submit", {
    method: "POST",
    body: new FormData(form),
  });
  const payload = await response.json();
  if (payload.success) {
    window.location.href = `/success/${payload.submission_id}`;
    return;
  }
  alert(`Please complete required fields: ${(payload.errors || []).join(", ")}`);
  submitBtn.disabled = false;
  spinner.classList.add("d-none");
});

showStep(currentStep);
