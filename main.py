from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncio
from g4f.client import Client
from g4f.Provider import (
    Acytoo, Aichatos, Ails, AItianhu, Bard, Bing, ChatBase,
    ChatForAi, Chatgpt4Online, CodeLinkAva, DeepAi, FreeGpt, FreeNetfly,
    Gemini, H2o, Koala, Liaobots, Miku, Myshell, Phind, Raycast,
    Replit, Theb, Vercel, Vitalentum, You, Yqcloud, GPTalk, GptGo, GptGod,
    Acytoo, Blackbox, DeepInfra, HuggingFace, OpenaiChat, OpenaiChatFree,
    OpenAssistant, AiAsk, ChatgptNext, ChatHub, FreeGpt35, GptForLove, DuckDuckGo
)

app = FastAPI()
client = Client()

# 🧠 Try these models (some use different internal mappings)
MODELS = [
    "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo-free", "llama-3-8b",
    "blackbox", "mistral-7b", "deepseek-coder", "mythomax", "phi-3-mini"
]

# ⚙️ All available providers — you can expand this list as needed
PROVIDERS = [
    Acytoo, Aichatos, Ails, AItianhu, Bard, Bing, ChatBase,
    ChatForAi, CodeLinkAva, DeepAi, FreeGpt, FreeNetfly,
    Gemini, H2o, Koala, Liaobots, Miku, Myshell, Phind,
    Raycast, Replit, Theb, Vercel, Vitalentum, You, Yqcloud,
    GPTalk, GptGo, GptGod, Blackbox, DeepInfra, HuggingFace,
    OpenaiChatFree, OpenAssistant, AiAsk, ChatgptNext, ChatHub,
    FreeGpt35, GptForLove, DuckDuckGo
]

# 🚀 Try every model-provider combination and return first success
async def try_all_models(text: str):
    async def try_one(provider, model):
        try:
            print(f"⚙️ Trying {provider.__name__} with {model}...")
            response = client.chat.completions.create(
                model=model,
                provider=provider,
                messages=[
                    {"role": "system", "content": "Summarize the given security vulnerability clearly and briefly."},
                    {"role": "user", "content": text}
                ],
            )
            summary = response.choices[0].message.content.strip()
            if summary:
                print(f"✅ Success with {provider.__name__} / {model}")
                return f"{provider.__name__} ({model})", summary
        except Exception as e:
            print(f"❌ {provider.__name__} / {model} failed: {e}")
        return None

    tasks = [try_one(provider, model) for provider in PROVIDERS for model in MODELS]
    for coro in asyncio.as_completed(tasks):
        result = await coro
        if result:
            return result
    return None, None

@app.post("/summarize")
async def summarize(request: Request):
    data = await request.json()
    text = data.get("text", "")
    if not text:
        return JSONResponse({"error": "No text provided"}, status_code=400)

    provider_model, summary = await try_all_models(text)
    if not summary:
        return JSONResponse({"error": "All models/providers failed"}, status_code=500)

    return JSONResponse({
        "provider": provider_model,
        "summary": summary
    })
