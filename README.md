# 🥗 КалоРій — Аналіз калорійності та КБЖУ (Gemini)

## 🚀 Запуск

### 1. Встановіть залежності
```bash
pip install -r requirements.txt
```

### 2. Отримайте безплатний Gemini API ключ
1. Перейдіть на https://aistudio.google.com/
2. Натисніть "Get API key" → "Create API key"
3. Скопіюйте ключ

### 3. Встановіть ключ і запустіть

**macOS / Linux:**
```bash
export OPENAI_API_KEY="your-key-here"
uvicorn main:app --reload
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=your-key-here
uvicorn main:app --reload
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-key-here"
uvicorn main:app --reload
```

### 4. Відкрийте браузер
```
http://localhost:8000
```

## 💡 Безплатні ліміти Gemini
- 15 запитів / хвилину
- 1500 запитів / день
- Повністю безплатно
