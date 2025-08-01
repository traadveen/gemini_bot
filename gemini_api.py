import requests
import time
from config import GEMINI_API_URL, GEMINI_API_KEY
from limit_tracker import update_limits

def count_tokens(text):
    # Примерная оценка: 1 токен ≈ 4 символа
    return len(text) // 4

def ask_gemini(messages, max_retries=4, retry_delay=5):
    prompt_tokens = sum(count_tokens(m["text"]) for m in messages)
    allowed, reason = update_limits(prompt_tokens)
    if not allowed:
        return reason

    system_prompt = {
        "role": "user",
        "text": (
            "Ты мой лучший друг с измайлово. Ты очень дружелюбный и всегда готов помочь, с уличным юмором, на сленге, как будто ты брат с района. "
            "Будь энергичным, но дружелюбным, можешь вставлять шутки, прибаутки, фразы типа 'йоу', 'бро', 'че как', "
            "'ща сделаю тебе красиво', 'слышь, брат', 'ща разрулим'. Не отвечай как обычный бот, не будь формальным."
        )
    }

    full_messages = [system_prompt] + messages[-20:]  # не перегружаем

    payload = {
        "contents": [{"role": m["role"], "parts": [{"text": m["text"]}]} for m in full_messages]
    }

    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                GEMINI_API_URL + f"?key={GEMINI_API_KEY}",
                json=payload
            )

            if response.status_code == 503:
                if attempt < max_retries:
                    time.sleep(retry_delay)
                    continue
                else:
                    return "меня временно заблокировали в интернете, попоробуй позже (503)"

            if response.status_code != 200:
                return f"Ошибка Gemini: {response.status_code} — {response.text}"

            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            return f"Ошибка соединения {e}"

    return "Не удалось получить ответ от Gemini после нескольких попыток."
