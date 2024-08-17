import unittest
from unittest.mock import MagicMock, patch

from guard.clients import BaseAIClient, CustomAIClient, GoogleClient, OpenAIClient


class TestAIClients(unittest.TestCase):
    def test_base_ai_client_instantiation(self):
        with self.assertRaises(NotImplementedError):
            BaseAIClient()

    def test_base_ai_client_scan_code(self):
        class TestClient(BaseAIClient):
            pass

        with self.assertRaises(NotImplementedError):
            TestClient().scan_code()

    @patch("guard.clients.openai.OpenAI")
    @patch("os.getenv", return_value="fake_openai_api_key")
    def test_openai_client_scan_code(self, mock_getenv, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="Mocked OpenAI response"))
        ]

        client = OpenAIClient(model="fake_model")
        result = client.scan_code("sample code")

        self.assertEqual(result, "Mocked OpenAI response")
        mock_client.chat.completions.create.assert_called_once()

    @patch("guard.clients.genai.GenerativeModel")
    @patch("guard.clients.genai.configure")
    @patch("os.getenv", return_value="fake_gemini_api_key")
    def test_google_client_scan_code(
        self, mock_getenv, mock_configure, mock_generative_model
    ):
        mock_model = MagicMock()
        mock_generative_model.return_value = mock_model
        mock_model.generate_content.return_value.text = "Mocked Google Gemini response"

        client = GoogleClient(model="fake_model")
        result = client.scan_code("sample code")

        self.assertEqual(result, "Mocked Google Gemini response")
        mock_model.generate_content.assert_called_once()

    @patch("requests.post")
    def test_custom_ai_client_scan_code(self, mock_post):
        mock_response = MagicMock()
        mock_post.return_value = mock_response
        mock_response.json.return_value = {
            "message": {"content": "Mocked Custom AI response"}
        }
        mock_response.raise_for_status.return_value = None

        client = CustomAIClient(
            model="fake_model", host="http://localhost", port="8000", token="fake_token"
        )
        result = client.scan_code("sample code")

        self.assertEqual(result, "Mocked Custom AI response")

        actual_content = mock_post.call_args[1]["json"]["messages"][0]["content"]
        self.assertIn("carefully reviewing the following code", actual_content)
        self.assertIn("provide clear and actionable recommendations", actual_content)
        self.assertIn("sample code", actual_content)


if __name__ == "__main__":
    unittest.main()
