# llm_agent/tool_youtube.py

import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


class YoutubeTranscriptTool:
    """Инструмент для получения транскрипции YouTube видео и её суммаризации."""

    name = "youtube_transcript"
    description = "Получает транскрипцию видео с YouTube по ссылке и возвращает её краткое содержание через локальную LLM."

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "qwen3.5"):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model

    def use(self, video_url: str) -> str:
        """Принимает ссылку на YouTube, возвращает суммаризацию транскрипции."""
        try:
            # 1. Извлекаем video_id
            url = video_url.strip()
            if "youtu.be" in url:
                video_id = url.split("/")[-1].split("?")[0]
            elif "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "embed/" in url:
                video_id = url.split("embed/")[1].split("?")[0]
            elif "/shorts/" in url:
                video_id = url.split("/shorts/")[1].split("?")[0]
            else:
                return f"Не удалось извлечь video_id из ссылки: {url}"

            print(f"> Получаю транскрипцию видео {video_id}...")
            transcript = YouTubeTranscriptApi().fetch(video_id)
            text = " ".join(seg.text for seg in transcript)
            print(f"> Транскрипция получена ({len(text)} символов). Суммаризирую...")

            # 2. Суммаризация через Ollama
            prompt = f"Сделай краткое резюме следующего текста на русском языке:\n\n{text}"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 500},
            }
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=60)
            response.raise_for_status()
            summary = response.json().get("response", "").strip()
            print("> Суммаризация готова.")
            return summary

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            return f"Транскрипция недоступна: {e}"
        except Exception as e:
            return f"Ошибка при обработке YouTube: {e}"# llm_agent/tool_youtube.py

import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


class YoutubeTranscriptTool:
    """Инструмент для получения транскрипции YouTube видео и её суммаризации."""

    name = "youtube_transcript"
    description = "Получает транскрипцию видео с YouTube по ссылке и возвращает её краткое содержание через локальную LLM."

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "qwen3.5"):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model

    def use(self, video_url: str) -> str:
        """Принимает ссылку на YouTube, возвращает суммаризацию транскрипции."""
        try:
            # 1. Извлекаем video_id
            url = video_url.strip()
            if "youtu.be" in url:
                video_id = url.split("/")[-1].split("?")[0]
            elif "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "embed/" in url:
                video_id = url.split("embed/")[1].split("?")[0]
            elif "/shorts/" in url:
                video_id = url.split("/shorts/")[1].split("?")[0]
            else:
                return f"Не удалось извлечь video_id из ссылки: {url}"

            # 2. Получаем транскрипцию
            print(f"> Получаю транскрипцию видео {video_id}...")
            try:
                transcript = YouTubeTranscriptApi().fetch(video_id)
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                return f"Транскрипция недоступна: {e}"

            text = " ".join(seg.text for seg in transcript)
            print(f"> Транскрипция получена ({len(text)} символов). Суммаризирую через {self.model}...")

            # 3. Суммаризация через Ollama
            prompt = (
                "Сделай краткое резюме следующего текста на русском языке "
                f"(не более 500 символов):\n\n{text}"
            )
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 500},
            }
            response = requests.post(
                f"{self.ollama_url}/api/generate", json=payload, timeout=60
            )
            response.raise_for_status()
            summary = response.json().get("response", "").strip()
            print("> Суммаризация готова.")
            return summary

        except Exception as e:
            print(f"> Ошибка при обработке YouTube: {e}")
            return f"Произошла ошибка при обработке видео '{video_url}': {e}"