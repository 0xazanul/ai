from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from gpt4free import forefront  # or another available provider

app = FastAPI()

@app.post("/summarize")
async def summarize(request: Request):
    data = await request.json()
    text = data.get("text", "")

    if not text:
        return JSONResponse({"error": "No text provided"}, status_code=400)

    # Use gpt4free provider
    try:
        summary = ""
        for token in forefront.StreamingCompletion.create(
            model='gpt-4',
            prompt=f"Summarize this report clearly and concisely:\n{text}"
        ):
            summary += token.choices[0].text
        return {"summary": summary.strip()}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
