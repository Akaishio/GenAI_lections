# main.py

from llm_agent.core_v2 import LLMAgent

def main():
    """Основная функция для запуска агента."""
    print("Простой LLM-агент с инструментами ('Калькулятор', 'Поиск в DuckDuckGo', 'YouTube')")
    print("-" * 70)

    #agent = LLMAgent(model = "qwen/qwen3-next-80b-a3b-instruct:free")

    agent = LLMAgent(local = True, ollama_model = "qwen3.5") 
    #ollama_base_url = "10.10.34.24:5678"

    #agent = LLMAgent(model = "gpt-5.4-mini")
    #agent = LLMAgent(model = "grok4.1-fast")
    
    # Примеры запросов
    # query = "Сколько будет (5 + 3) * 2?"
    # query = "Какая погода в Москве?"
    query =     query = "Сколько будет (5 + 3) * 2? И сделай краткое содержание видео https://youtu.be/y3MzPLP53sA"

    print(f"Ваш запрос: {query}")
    print("-" * 70)

    response = agent.process_query(query)

    print("\n" + "=" * 70)
    print("Финальный ответ агента:\n")
    print(response)
    print("=" * 70)


if __name__ == "__main__":
    main()

# ============================================================
# Проверка YoutubeTranscriptTool
# ============================================================
print("\n" + "=" * 70)
print("Проверка YoutubeTranscriptTool")


from llm_agent.tool_youtube import YoutubeTranscriptTool

# Создаём инструмент с локальной моделью qwen3.5
tool = YoutubeTranscriptTool(
    ollama_url="http://localhost:11434",
    model="qwen3.5"
)

# Ссылка на видео с субтитрами (можно заменить)
video_url = "https://youtu.be/y3MzPLP53sA?si=OrsYkanaPjpIScHt"

try:
    # Получаем транскрипцию (без Ollama)
    print("Получаю транскрипцию...")
    transcript = tool.get_transcript(video_url, languages=['ru', 'en'])
    print(f"Транскрипция получена! Длина: {len(transcript)} символов")
    print("Первые 300 символов транскрипции:")
    print(transcript[:300])

    # Суммаризируем через Ollama
    print("\nСуммаризирую через модель qwen3.5:0.8b...")
    summary = tool.summarize_text(transcript, max_length=300)
    print("\n=== СУММАРИЗАЦИЯ ===")
    print(summary)

except Exception as e:
    print(f"Ошибка: {e}")