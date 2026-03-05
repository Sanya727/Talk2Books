const LANG_MAP = {
  en: "en",
  hi: "hi",
  pa: "pa",
  english: "en",
  hindi: "hi",
  punjabi: "pa"
};

function normalizeLang(val) {
  if (!val) return "";
  const k = val.toString().trim().toLowerCase();
  return LANG_MAP[k] || "";
}

async function uploadFiles() {
  const files = document.getElementById("fileInput").files;
  const status = document.getElementById("uploadStatus");

  if (files.length === 0) {
    alert("Please select at least one file!");
    return;
  }
  if (files.length > 5) {
    alert("You can upload a maximum of 5 files!");
    return;
  }

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append(`file${i}`, files[i]);
  }

  status.innerText = "⏳ Uploading...";

  try {
    const res = await fetch("http://localhost:5000/upload", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    if (res.ok) {
      status.innerText = "✅ Uploaded Successfully!";
      document.getElementById("lang-section").style.display = "block";
      document.getElementById("chat-section").style.display = "block";
      window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
    } else {
      status.innerText = "❌ Upload Failed: " + (data.error || "Unknown error");
    }
  } catch (err) {
    status.innerText = "❌ Upload Error: " + err.message;
  }
}

async function askQuestion() {
  const question = document.getElementById("question").value.trim();
  const rawQLang = document.getElementById("questionLang").value;
  const rawALang = document.getElementById("answerLang").value;
  const responseDiv = document.getElementById("response");

  const questionLang = normalizeLang(rawQLang);
  const answerLang = normalizeLang(rawALang);

  if (!question) {
    alert("Please enter a question!");
    return;
  }
  if (!questionLang || !answerLang) {
    alert("Invalid language selection. Pick English / Hindi / Punjabi again.");
    return;
  }

  responseDiv.innerHTML = `
    <div style="padding:10px;background:#0f172a;border-radius:8px;color:#facc15;">
      💭 Thinking…<br>
      <small>Sending → question_lang: <b>${questionLang}</b>, answer_lang: <b>${answerLang}</b></small>
    </div>
  `;

  try {
    const res = await fetch("http://localhost:5000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        question_lang: questionLang,
        answer_lang: answerLang,
      }),
    });

    const data = await res.json();

    if (res.ok && data.answer) {
      const answerText = typeof data.answer === "string" ? data.answer : JSON.stringify(data.answer);
      const sourceText = data.source ? `<br><br>📘 <b>Source:</b> ${data.source}` : "";

      responseDiv.innerHTML = `
        <div style="padding:12px;background:#1e293b;border-radius:8px;color:#e2e8f0;">
          <strong>🧾 Answer:</strong><br>${answerText}${sourceText}
        </div>
      `;
    } else {
      responseDiv.innerHTML = `
        <div style="padding:12px;background:#1e293b;border-radius:8px;color:#f87171;">
          ❌ ${data.error || "No relevant information found in the uploaded files."}
        </div>
      `;
    }

    // auto-scroll down when answer appears
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });

  } catch (err) {
    responseDiv.innerHTML = `
      <div style="padding:12px;background:#1e293b;border-radius:8px;color:#f87171;">
        ⚠️ Network Error: ${err.message}
      </div>
    `;
  }
}
