const form = document.querySelector("#question-form");
const input = document.querySelector("#question-input");
const conversation = document.querySelector("#conversation");
const askButton = form.querySelector("button[type='submit']");

function addMessage(kind, text) {
  const message = document.createElement("div");
  message.className = `chat-message ${kind}`;
  message.textContent = text;
  conversation.appendChild(message);
  message.scrollIntoView({ behavior: "smooth", block: "nearest" });
  return message;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = input.value.trim();
  if (!question) return;

  addMessage("user-message", question);
  input.value = "";
  askButton.disabled = true;

  const waiting = addMessage(
    "assistant-message",
    "Checking local trip records…",
  );

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "The question could not be answered.");
    }

    waiting.textContent = data.answer;
  } catch (error) {
    waiting.textContent = `Sorry, I couldn't get an answer: ${error.message}`;
  } finally {
    askButton.disabled = false;
    input.focus();
  }
});

document.querySelectorAll(".suggestion").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.textContent.trim();
    form.requestSubmit();
  });
});
async function loadTripSummary() {
  try {
    const response = await fetch("/api/summary");
    if (!response.ok) throw new Error("Could not load trip summary.");

    const data = await response.json();

    document.querySelector("#trip-count").textContent = data.trip_count;
    document.querySelector("#trip-period").textContent = data.period;
    document.querySelector("#weeks-covered").textContent =
      `${data.weeks_covered} weeks`;
    document.querySelector("#energy-use").textContent =
      `${data.energy_per_100_km} kWh`;
    document.querySelector("#distance-total").textContent =
      `${data.distance_km} km total distance`;
  } catch (error) {
    document.querySelector("#trip-period").textContent = error.message;
  }
}

loadTripSummary();
