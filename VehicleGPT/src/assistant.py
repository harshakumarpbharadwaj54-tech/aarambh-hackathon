import io
import json
from contextlib import redirect_stdout
from urllib.request import Request, urlopen

from analytics import compare_periods


def answer_question(question):
    supported_words = ["range", "energy", "consumption", "efficiency"]

    if not any(word in question.lower() for word in supported_words):
        return (
            "I don't have enough information to answer that yet. "
            "Try asking about range or energy use."
        )

    # Get the figures from your own trip analysis.
    result = io.StringIO()
    with redirect_stdout(result):
        compare_periods()

    facts = result.getvalue().strip()

    if not facts:
        return "I couldn't find trip records to answer this question."

    # Ask the local model to explain only those figures.
    payload = {
        "model": "local-model",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You explain vehicle data using only the supplied trip analysis. "
                    "Do not guess why a change happened. Do not add factors that are not "
                    "listed in the analysis. Say that a cause is unknown unless the data "
                    "proves it. Answer in at most 3 short sentences. Finish the answer."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Driver's question: {question}\n\n"
                    f"Trip analysis:\n{facts}"
                ),
            },
        ],
        "temperature": 0,
        "max_tokens": 120,
    }

    request = Request(
        "http://127.0.0.1:8081/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            answer = json.loads(response.read().decode("utf-8"))
        explanation = answer["choices"][0]["message"]["content"].strip()
        return explanation
    except Exception:
        # Keep the app useful if the local model server is unavailable.
        return (
            "VehicleGPT checked the saved trip records, but couldn't reach "
            "the local language model. Here are the analysis results:\n\n"
            + facts
        )