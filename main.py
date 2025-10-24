from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from g4f.client import Client

app = FastAPI()

@app.post("/summarize")
async def summarize(request: Request):
    data = await request.json()
    text = data.get("text", "")
    if not text:
        return JSONResponse({"error": "No text provided"}, status_code=400)

    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful report summarizer."},
                {"role": "user", "content": f"Summarize this report clearly:\n{text}"}
            ]
        )
        summary = response.choices[0].message.content
        return {"summary": summary.strip()}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
