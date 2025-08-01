# limit_tracker.py

import time
import json
from threading import Lock
from config import MAX_REQUESTS_PER_MINUTE, MAX_REQUESTS_PER_DAY, MAX_TOKENS_PER_MINUTE

state_file = "state.json"
lock = Lock()

# Стартовое состояние
default_state = {
    "minute": {"time": 0, "count": 0, "tokens": 0},
    "day": {"time": 0, "count": 0},
    "history": {}  # чат_id: [сообщения]
}

def load_state():
    try:
        with open(state_file, "r") as f:
            return json.load(f)
    except:
        return default_state.copy()

def save_state(state):
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

def get_state():
    with lock:
        return load_state()

def update_limits(request_tokens):
    with lock:
        state = load_state()
        now = time.time()
        minute = state["minute"]
        day = state["day"]

        # Обновить минутный счётчик
        if now - minute["time"] >= 60:
            minute["time"] = now
            minute["count"] = 0
            minute["tokens"] = 0

        # Обновить дневной счётчик
        if now - day["time"] >= 86400:
            day["time"] = now
            day["count"] = 0

        # Проверка лимитов
        if minute["count"] >= MAX_REQUESTS_PER_MINUTE:
            return False, "Достигнут лимит запросов в минуту."
        if minute["tokens"] + request_tokens >= MAX_TOKENS_PER_MINUTE:
            return False, "Достигнут лимит токенов в минуту."
        if day["count"] >= MAX_REQUESTS_PER_DAY:
            return False, "Достигнут дневной лимит запросов."

        # Обновление счётчиков
        minute["count"] += 1
        minute["tokens"] += request_tokens
        day["count"] += 1

        save_state(state)
        return True, None

def get_history(chat_id):
    state = get_state()
    return state["history"].get(str(chat_id), [])

def append_to_history(chat_id, user_message, bot_reply):
    with lock:
        state = load_state()
        history = state["history"].get(str(chat_id), [])
        history.append({"role": "user", "text": user_message})
        history.append({"role": "model", "text": bot_reply})
        # ограничим по числу сообщений (пар)
        if len(history) > 20:
            history = history[-20:]
        state["history"][str(chat_id)] = history
        save_state(state)

def reset_history(chat_id):
    with lock:
        state = load_state()
        state["history"][str(chat_id)] = []
        save_state(state)
