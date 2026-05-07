import base64
import json
import os
import re
import httpx
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Calorie Analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_URL = "https://api.openai.com/v1/responses"

SYSTEM_PROMPT = """Ти — точний нутриціолог та дієтолог. Аналізуй їжу та повертай ТІЛЬКИ JSON без жодного додаткового тексту, без ```json, без пояснень.

Формат відповіді (строго валідний JSON):
{
  "dish_name": "Назва страви",
  "portion_grams": 300,
  "calories": 450,
  "protein": 25.5,
  "fat": 18.2,
  "carbs": 42.1,
  "fiber": 3.4,
  "ingredients": [
    {"name": "Куряча грудка", "grams": 150, "calories": 165},
    {"name": "Рис варений", "grams": 100, "calories": 130}
  ],
  "confidence": "high",
  "notes": "Коротка примітка про страву або точність оцінки"
}

Правила:
- Всі числа — з одним знаком після коми
- portion_grams — реалістична порція в грамах
- confidence: "high" | "medium" | "low"
- Якщо не можеш точно визначити — вкажи confidence "low" і наближені значення
- ТІЛЬКИ валідний JSON, ніяких пояснень поза JSON"""


def parse_response(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def call_openai(input_content) -> dict:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY не встановлено.")

    payload = {
        "model": "gpt-5.4-mini",
        "instructions": SYSTEM_PROMPT,
        "input": input_content,
        "store": True,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            OPENAI_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json=payload,
        )

    if resp.status_code != 200:
        print("OpenAI error:", resp.text)
        raise HTTPException(status_code=502, detail=f"OpenAI API помилка: {resp.text}")

    data = resp.json()
    text = data["output"][0]["content"][0]["text"]
    return parse_response(text)


@app.post("/analyze/text")
async def analyze_text(description: str = Form(...)):
    return await call_openai(f"Проаналізуй цю їжу і дай точні КБЖУ: {description}")


@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    contents = await file.read()
    image_data = base64.standard_b64encode(contents).decode("utf-8")
    media_type = file.content_type or "image/jpeg"

    input_content = [
        {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": f"data:{media_type};base64,{image_data}"
                },
                {
                    "type": "input_text",
                    "text": "Визнач що на фото і дай точні КБЖУ для цієї порції їжі."
                }
            ]
        }
    ]
    return await call_openai(input_content)


app.mount("/", StaticFiles(directory="static", html=True), name="static")