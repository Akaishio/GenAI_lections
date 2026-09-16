import sys
import os
# Добавляем путь к папке, где лежит пакет llm_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '3_1_LLM_agent')))

import pytest
from unittest.mock import patch, MagicMock
from llm_agent.tool_youtube import YoutubeTranscriptTool

# Тест 1: извлечение video_id из разных форматов ссылок
def test_extract_video_id():
    tool = YoutubeTranscriptTool()
    assert tool.extract_video_id("https://youtu.be/abc123?t=10") == "abc123"
    assert tool.extract_video_id("https://www.youtube.com/watch?v=abc123") == "abc123"
    assert tool.extract_video_id("https://www.youtube.com/embed/abc123") == "abc123"
    with pytest.raises(ValueError):
        tool.extract_video_id("https://example.com")

# Тест 2: успешное получение транскрипции с моком API
@patch("llm_agent.tool_youtube.YouTubeTranscriptApi.fetch")
def test_get_transcript_success(mock_fetch):
    mock_segment1 = MagicMock()
    mock_segment1.text = "Привет мир"
    mock_segment2 = MagicMock()
    mock_segment2.text = "Это тест"
    mock_fetch.return_value = [mock_segment1, mock_segment2]

    tool = YoutubeTranscriptTool()
    result = tool.get_transcript("https://youtu.be/abc123")
    assert result == "Привет мир Это тест"
    mock_fetch.assert_called_once()

# Тест 3: обработка ошибки при недоступной транскрипции
@patch("llm_agent.tool_youtube.YouTubeTranscriptApi.fetch")
def test_get_transcript_error(mock_fetch):
    from youtube_transcript_api._errors import TranscriptsDisabled
    mock_fetch.side_effect = TranscriptsDisabled("disabled")
    
    tool = YoutubeTranscriptTool()
    with pytest.raises(RuntimeError):
        tool.get_transcript("https://youtu.be/abc123")

# Тест 4: суммаризация через мок requests.post
@patch("llm_agent.tool_youtube.requests.post")
def test_summarize_text(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Краткое содержание"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    tool = YoutubeTranscriptTool(ollama_url="http://fake:11434", model="test")
    result = tool.summarize_text("Длинный текст для теста")
    assert result == "Краткое содержание"
    mock_post.assert_called_once()

# Тест 5 (опционально): метод use
@patch("llm_agent.tool_youtube.YoutubeTranscriptTool.get_transcript")
@patch("llm_agent.tool_youtube.YoutubeTranscriptTool.summarize_text")
def test_use_method(mock_summarize, mock_get_transcript):
    mock_get_transcript.return_value = "Транскрипция"
    mock_summarize.return_value = "Суммаризация"

    tool = YoutubeTranscriptTool()
    result = tool.use("https://youtu.be/abc123")
    assert result == "Суммаризация"
    mock_get_transcript.assert_called_once_with("https://youtu.be/abc123")
    mock_summarize.assert_called_once_with("Транскрипция")