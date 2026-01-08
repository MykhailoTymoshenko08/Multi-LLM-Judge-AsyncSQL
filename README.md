# AI Aggregator-Judge

**AI Aggregator-Judge** — це консольний застосунок на Python, який порівнює відповіді двох різних мовних моделей (через API OpenRouter) і за допомогою третьої моделі-“судді” формує фінальну відповідь найвищої якості.  
Система зберігає історію запитів у локальну базу SQLite та веде статистику часу виконання кожної моделі.

---

## Основні можливості

- Паралельні запити до кількох моделей (асинхронно через `asyncio`)
- “Суддя” оцінює відповіді й генерує фінальну, об’єднану відповідь
- Автоматичне збереження запитів, відповідей і часу виконання у SQLite
- Перегляд статистики продуктивності моделей
- Підтримка історії повідомлень (контекстна пам’ять)
- Очищення пам’яті історії в один клік

---

## Використані технології

- **Python 3.10+**
- **LangChain**
- **SQLite3**
- **dotenv**
- **langchain-openai**
- **langchain-core**
- **OpenRouter API**
- **asyncio**

---

## Встановлення

### 1. Клонування репозиторію
```bash
git clone https://github.com/MykhailoTymoshenko08/Multi-LLM-Judge-AsyncSQL
cd ai-aggregator-judge
```

### 2. Створення та активація віртуального середовища
```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3. Встановлення залежностей
```bash
pip install -r requirements.txt
```

### Налаштування змінних середовища
Створи файл .env у кореневій директорії та додай свій ключ:
```bash
API_KEY=your_openrouter_api_key_here
```

## Використання

### Запуск застосунку:
```bash
python main.py
```
Після запуску побачиш головне меню:
```bash
==================================================
AI AGGREGATOR-JUDGE
==================================================

--- Model statistic ---
Model: meta-llama/llama-3.3-70b-instruct:free | Average time: 3.52s | Requests: 12
Model: google/gemma-3-27b-it:free | Average time: 2.88s | Requests: 12
Model: mistralai/devstral-2512:free_JUDGE | Average time: 1.97s | Requests: 12

==================================================
MENU:
1. Ask question
2. Show detailed statistic
3. Clear memory
4. Exit
==================================================
```

### Приклад роботи
Обери пункт 1 — Ask question
Введи своє запитання, наприклад:
```bash
Enter your request: Explain the concept of reinforcement learning.
```
Програма:
1. надсилає запит до Meta LLaMA 3.3 та Gemma 3
2. отримує дві незалежні відповіді
3. передає їх моделі-“судді” (Mistral DevStral) для створення фінального результату
Вивід:
```bash
==================================================
Original answers:
Model 1: ✅[LLaMA's response...]
==================================================
Model 2: ✅[Gemma's response...]
==================================================

Final answer:
✅Reinforcement learning is a branch of machine learning...
```
