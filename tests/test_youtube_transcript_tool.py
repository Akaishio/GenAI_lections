import pytest
from unittest.mock import patch, MagicMock
from tools.youtube_transcript_tool import YoutubeTranscriptTool

# Тест 1: извлечение video_id из разных форматов ссылок
def test_extract_video_id():
    tool = YoutubeTranscriptTool()
    assert tool.extract_video_id("https://youtu.be/abc123?t=10") == "abc123"
    assert tool.extract_video_id("https://www.youtube.com/watch?v=abc123") == "abc123"
    assert tool.extract_video_id("https://www.youtube.com/embed/abc123") == "abc123"
    with pytest.raises(ValueError):
        tool.extract_video_id("https://example.com")

# Тест 2: успешное получение транскрипции с моком API
@patch("tools.youtube_transcript_tool.YouTubeTranscriptApi.fetch")
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
@patch("tools.youtube_transcript_tool.YouTubeTranscriptApi.fetch")
def test_get_transcript_error(mock_fetch):
    from youtube_transcript_api._errors import TranscriptsDisabled
    mock_fetch.side_effect = TranscriptsDisabled("disabled")
    
    tool = YoutubeTranscriptTool()
    with pytest.raises(RuntimeError):
        tool.get_transcript("https://youtu.be/abc123")

# Тест 4: суммаризация через мок requests.post
@patch("tools.youtube_transcript_tool.requests.post")
def test_summarize_text(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Краткое содержание"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    tool = YoutubeTranscriptTool(ollama_url="http://fake:11434", model="test")
    result = tool.summarize_text("Длинный текст для теста")
    assert result == "Краткое содержание"
    mock_post.assert_called_once()