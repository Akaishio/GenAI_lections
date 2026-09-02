import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

class YoutubeTranscriptTool:
    """Инструмент для получения и суммаризации транскрипции YouTube видео."""

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.1"):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model

    @staticmethod
    def extract_video_id(url: str) -> str:
        if "youtu.be" in url:
            return url.split("/")[-1].split("?")[0]
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        if "embed/" in url:
            return url.split("embed/")[1].split("?")[0]
        raise ValueError("Не удалось извлечь video_id из ссылки")

    def get_transcript(self, video_url: str, languages: list = None) -> str:
        video_id = self.extract_video_id(video_url)
        try:
            api = YouTubeTranscriptApi()
            if languages:
                transcript = api.fetch(video_id, languages=languages)
            else:
                transcript = api.fetch(video_id)
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            raise RuntimeError(f"Транскрипция недоступна: {e}")

        full_text = " ".join(segment.text for segment in transcript)
        return full_text

    def summarize_text(self, text: str, max_length: int = 500) -> str:
        prompt = (
            f"Сделай краткое резюме следующего текста на русском языке "
            f"(не более {max_length} символов):\n\n{text}"
        )
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": max_length}
        }
        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.RequestException as e:
            raise RuntimeError(f"Ошибка при обращении к Ollama: {e}")