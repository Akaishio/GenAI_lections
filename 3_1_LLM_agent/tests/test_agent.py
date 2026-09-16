import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, patch
from llm_agent.core_v2 import LLMAgent
from llm_agent.tool_youtube import YoutubeTranscriptTool

# =====================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ (Запускают реальную Ollama / API)
# =====================================================================
# Маркируем как 'integration', чтобы их можно было отключать при быстрой проверке

@pytest.mark.integration
def test_calculator_query_live():
    """Реальный запуск агента для проверки математики."""
    # Для тестов лучше использовать локальную модель, если она поднята
    agent = LLMAgent(local=True, ollama_model="qwen3:4b")
    query = "Сколько будет (5 + 3) * 2? Напиши только цифру."
    
    response = agent.process_query(query)
    
    # Проверяем, что агент смог посчитать и выдать 16
    assert "16" in response


@pytest.mark.integration
def test_football_query_live():
    """Реальный запуск агента для проверки поиска DuckDuckGo."""
    agent = LLMAgent(local=True, ollama_model="qwen3:4b")
    query = "Кто выиграл последний матч Спартак-Динамо?"
    
    response = agent.process_query(query)
    
    # Проверяем, что в реальном ответе фигурируют нназвания команд
    assert "Спартак" in response or "Spartak" in response
    assert "Динамо" in response or "Dynamo" in response
# =====================================================================
# ЮНИТ-ТЕСТЫ ДЛЯ YoutubeTranscriptTool (с моками, без сети)
# =====================================================================

def test_youtube_use_success():
    """Успешное получение транскрипции и суммаризация для ссылки youtu.be."""
    with patch("llm_agent.tool_youtube.YouTubeTranscriptApi.fetch") as mock_fetch, \
         patch("llm_agent.tool_youtube.requests.post") as mock_post:
        seg1, seg2 = MagicMock(), MagicMock()
        seg1.text = "Привет"
        seg2.text = "мир"
        mock_fetch.return_value = [seg1, seg2]

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Краткое содержание"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        tool = YoutubeTranscriptTool(model="test")
        result = tool.use("https://youtu.be/abc123?t=10")

        assert result == "Краткое содержание"
        mock_fetch.assert_called_once()
        mock_post.assert_called_once()


def test_youtube_use_invalid_url():
    """Обработка неверной ссылки (не удалось извлечь video_id)."""
    tool = YoutubeTranscriptTool()
    result = tool.use("https://example.com/video")
    assert "Не удалось извлечь video_id" in result


def test_youtube_use_transcript_disabled():
    """Обработка ошибки недоступной транскрипции."""
    from youtube_transcript_api._errors import TranscriptsDisabled
    with patch("llm_agent.tool_youtube.YouTubeTranscriptApi.fetch") as mock_fetch:
        mock_fetch.side_effect = TranscriptsDisabled("disabled")
        tool = YoutubeTranscriptTool()
        result = tool.use("https://youtu.be/abc123")
        assert "Транскрипция недоступна" in result


# =====================================================================
# Обёртка — вызывает все юнит-тесты внутри одной функции
# (требование: "вызвать их внутри отдельной тестовой функции")
# =====================================================================

def test_all_youtube_unit_tests():
    """Вызывает все юнит-тесты YoutubeTranscriptTool в одной функции."""
    test_youtube_use_success()
    test_youtube_use_invalid_url()
    test_youtube_use_transcript_disabled()
