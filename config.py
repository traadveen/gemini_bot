# config.py
import os
BOT_TOKEN =
GEMINI_API_KEY =
# Лимиты Gemini 1.5 Flash
MAX_REQUESTS_PER_MINUTE = 15
MAX_REQUESTS_PER_DAY = 1500
MAX_TOKENS_PER_MINUTE = 1_000_000

# Максимальная длина истории (примерно по токенам)
MAX_HISTORY_TOKENS = 3000

# Gemini endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
