// ---------------------------------------------------------------------------
// FRONTEND — presentation only.
// This file holds question TEXT and ORDER (for the interview flow) and the
// "why am I being asked this" copy. It does NOT decide malaria/typhoid/
// referral — every diagnostic decision is made by kbs_engine.py on the
// server, via a POST to /diagnose. This file only collects yes/no answers
// and renders whatever the backend returns.
// ---------------------------------------------------------------------------

const EMERGENCY = [
  { id: "impaired_consciousness", rule: "R-EMG-01", text: "Is the patient confused, disoriented, drowsy, or unresponsive?" },
  { id: "too_weak", rule: "R-EMG-02", text: "Is the patient too weak to sit, stand, or walk without assistance?" },
  { id: "seizures", rule: "R-EMG-03", text: "Has the patient had any seizures?" },
  { id: "rapid_breathing", rule: "R-EMG-04", text: "Is the patient breathing rapidly or with visible difficulty?" },
  { id: "yellow_skin", rule: "R-EMG-05", text: "Is there yellowing of the eyes or skin (jaundice)?" },
  { id: "bleeding", rule: "R-EMG-06", text: "Is there bleeding from the nose or gums, vomiting blood, or black stools?" },
  { id: "cold_extremities", rule: "R-EMG-07", text: "Are the patient's hands and feet unusually cold?" },
  { id: "severe_abdominal_pain", rule: "R-EMG-08", text: "Is there severe abdominal pain with tenderness or rigidity?" },
  { id: "swollen_abdomen", rule: "R-EMG-09", text: "Is the patient's abdomen swollen or distended?" },
  { id: "persistent_vomiting", rule: "R-EMG-10", text: "Is the patient vomiting persistently and unable to keep fluids down?" },
  { id: "severe_diarrhoea", rule: "R-EMG-11", text: "Does the patient have severe diarrhoea?" },
];

const CASE_ESTABLISHING = [
  { id: "fever", rule: "R-CASE-01", text: "Does the patient have a fever?" },
  { id: "headache", rule: "R-CASE-02", text: "Does the patient have a headache?" },
  { id: "fatigue_weakness", rule: "R-CASE-03", text: "Is the patient fatigued or generally weak?" },
  { id: "general_malaise", rule: "R-CASE-04", text: "Does the patient report general malaise (feeling unwell overall)?" },
  { id: "loss_of_appetite", rule: "R-CASE-05", text: "Has the patient lost their appetite?" },
];

const DISTINGUISHING = [
  { id: "chills", rule: "R-DIST-01", disease: "malaria", text: "Is the patient experiencing chills?" },
  { id: "sweating_after_fever", rule: "R-DIST-02", disease: "malaria", text: "Does the patient sweat heavily after the fever breaks?" },
  { id: "intermittent_fever", rule: "R-DIST-03", disease: "malaria", text: "Does the fever come and go in cycles, rather than stay constant?" },
  { id: "abdominal_pain", rule: "R-DIST-04", disease: "typhoid", text: "Does the patient have abdominal pain?" },
  { id: "constipation_adult", rule: "R-DIST-05", disease: "typhoid", text: "Is the patient constipated? (more typically seen in adults)" },
  { id: "diarrhoea_child", rule: "R-DIST-06", disease: "typhoid", text: "Does the patient have diarrhoea? (more typically seen in children)" },
  { id: "rose_spots", rule: "R-DIST-07", disease: "typhoid", text: "Are there flat, rose-coloured spots on the chest or abdomen?" },
  { id: "dry_cough_early", rule: "R-DIST-08", disease: "typhoid", text: "Did the patient have a dry cough early in the illness?" },
];

const ALL_QUESTIONS = EMERGENCY.map(q => ({ ...q, stage: "emergency" }))
  .concat(CASE_ESTABLISHING.map(q => ({ ...q, stage: "case" })))
  .concat(DISTINGUISHING.map(q => ({ ...q, stage: "dist" })));

let idx = 0;
let yesSymptoms = [];   // only the symptom ids answered "yes" — this is ALL we send to the backend
let log = [];

function currentQ() { return ALL_QUESTIONS[idx]; }

function whyFor(q) {
  if (q.stage === "emergency") {
    return `Rule ${q.rule} — Emergency stage. Emergency questions are checked first because patient safety takes priority over diagnosis. A "yes" here sends your answer to the server, which will immediately return an urgent-referral result without evaluating anything else.`;
  }
  if (q.stage === "case") {
    return `Rule ${q.rule} — Case-Establishing stage. This suggests the patient may have malaria or typhoid without distinguishing between them — the server won't attempt a diagnosis until at least one of these is confirmed "yes".`;
  }
  const other = q.disease === "malaria" ? "typhoid" : "malaria";
  return `Rule ${q.rule} — Distinguishing stage. This fact points toward ${q.disease}, not ${other}. The server uses these to tell the two diseases apart once a case has been established.`;
}

function renderLedger() {
  const body = document.getElementById("ledgerBody");
  if (log.length === 0) {
    body.innerHTML = '<div class="empty">No facts asserted yet.</div>';
    return;
  }
  body.innerHTML = log.map((e, i) =>
    `<div class="entry"><span class="n">${String(i + 1).padStart(2, "0")}</span>fact(${e.id}, "${e.val}")</div>`
  ).join("");
}

function renderQuestion() {
  const q = currentQ();
  const total = ALL_QUESTIONS.length;
  document.getElementById("progressFill").style.width = `${Math.round((idx / total) * 100)}%`;
  document.getElementById("mainPanel").innerHTML = `
    <div class="step-count">Question ${idx + 1} of ${total} — ${q.stage} stage</div>
    <span class="rule-id">${q.rule}</span>
    <p class="question">${q.text}</p>
    <div class="btn-row">
      <button id="btnYes">Yes</button>
      <button id="btnNo">No</button>
    </div>
    <button class="btn-why" id="btnWhy">why am I being asked this?</button>
    <div class="why-box" id="whyBox">${whyFor(q)}</div>
  `;
  document.getElementById("btnYes").onclick = () => answer("yes");
  document.getElementById("btnNo").onclick = () => answer("no");
  document.getElementById("btnWhy").onclick = () => document.getElementById("whyBox").classList.toggle("open");
}

function answer(val) {
  const q = currentQ();
  log.push({ id: q.id, val });
  renderLedger();
  if (val === "yes") yesSymptoms.push(q.id);

  // Early-exit on an emergency "yes" is a UI convenience only — the server
  // independently re-checks and will reach the same conclusion regardless.
  if (q.stage === "emergency" && val === "yes") {
    submitToBackend();
    return;
  }
  idx++;
  if (idx >= ALL_QUESTIONS.length) {
    submitToBackend();
  } else {
    renderQuestion();
  }
}

async function submitToBackend() {
  document.getElementById("progressFill").style.width = "100%";
  document.getElementById("mainPanel").innerHTML = `<div class="loading">Sending facts to the inference engine…</div>`;

  let data;
  try {
    const res = await fetch("/diagnose", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symptoms: yesSymptoms }),
    });
    if (!res.ok) throw new Error(`Server returned ${res.status}`);
    data = await res.json();
  } catch (err) {
    document.getElementById("mainPanel").innerHTML =
      `<div class="error">Could not reach the inference engine (${err.message}). Is app.py running?</div>`;
    return;
  }
  renderResult(data);
}

function renderResult(data) {
  document.getElementById("mainPanel").innerHTML = `
    <div class="result">
      <span class="flag">${data.result}</span>
      <h2>${data.heading}</h2>
      <p>${data.advice}</p>
      <details open>
        <summary>how was this decided? (server-side trace)</summary>
        ${data.explanation.map(l => `<div class="trace-line">${l}</div>`).join("")}
        <div class="trace-line"><b>Stage reached:</b> ${data.stage}</div>
      </details>
      <button id="btnRestart">start a new interview</button>
    </div>
  `;
  document.getElementById("btnRestart").onclick = restart;
}

function restart() {
  idx = 0; yesSymptoms = []; log = [];
  document.getElementById("progressFill").style.width = "0%";
  renderLedger();
  renderQuestion();
}

renderLedger();
renderQuestion();
