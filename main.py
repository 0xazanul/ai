from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from g4f.client import Client
import asyncio, os, uvicorn

app = FastAPI()
client = Client()

@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Summarizer API is running 🚀"}

# List of all providers/models to try
MODELS = [
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
    "gemini-pro",
    "claude-3-opus",
    "mixtral-8x7b",
    "phi-3-mini-128k",
]

async def try_model(model: str, text: str):
    """Try summarizing with one model; return result or raise exception."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert. Summarize this vulnerability report clearly and briefly."},
                {"role": "user", "content": text},
            ],
        )
        summary = response.choices[0].message.content.strip()
        if summary:
            return {"model": model, "summary": summary}
        raise ValueError("Empty response")
    except Exception as e:
        raise RuntimeError(f"{model} failed: {e}")

@app.post("/summarize")
async def summarize(request: Request):
    data = await request.json()
    text = data.get("text", "")
    if not text:
        return JSONResponse({"error": "No text provided"}, status_code=400)

    tasks = [asyncio.create_task(try_model(model, text)) for model in MODELS]

    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    # Cancel any remaining unfinished tasks
    for task in pending:
        task.cancel()

    for task in done:
        try:
            result = task.result()
            return {
                "success": True,
                "model_used": result["model"],
                "summary": result["summary"],
            }
        except Exception as e:
            continue

    return JSONResponse({"error": "All models failed to respond"}, status_code=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
