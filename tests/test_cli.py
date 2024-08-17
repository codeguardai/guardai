import unittest
from unittest.mock import MagicMock, patch

from guard.cli import format_as_markdown, initialize_client, scan


class TestFunctions(unittest.TestCase):
    @patch("guard.cli.OpenAIClient")
    def test_initialize_client_openai(self, mock_openai_client):
        initialize_client("openai", None)
        mock_openai_client.assert_called_once_with(model="gpt-4o-mini")

    @patch("guard.cli.GoogleClient")
    def test_initialize_client_google(self, mock_google_client):
        initialize_client("google", None)
        mock_google_client.assert_called_once_with(model="gemini-pro")

    @patch("guard.cli.CustomAIClient")
    def test_initialize_client_custom(self, mock_custom_client):
        initialize_client(
            "custom",
            "custom-model",
            "http://localhost",
            5000,
            "custom-token",
            "/api/v1/scan",
        )
        mock_custom_client.assert_called_once_with(
            model="custom-model",
            host="http://localhost",
            port=5000,
            token="custom-token",
            endpoint="/api/v1/scan",
        )

    @patch("guard.cli.scan_files")
    def test_scan_all_files(self, mock_scan_files):
        mock_scan_files.return_value = "Scan all files result"
        args = MagicMock(changes_only=False, directory=".")
        ai_client = MagicMock()
        result = scan(args, ai_client)
        self.assertEqual(result, "Scan all files result")
        mock_scan_files.assert_called_once_with(".", ai_client)

    @patch("guard.cli.scan_changes")
    def test_scan_changed_files(self, mock_scan_changes):
        mock_scan_changes.return_value = "Scan changed files result"
        args = MagicMock(
            changes_only=True,
            directory=".",
            repo="owner/repo",
            pr_number=1,
            github_token="token",
        )
        ai_client = MagicMock()
        result = scan(args, ai_client)
        self.assertEqual(result, "Scan changed files result")
        mock_scan_changes.assert_called_once_with(
            ".", ai_client, repo="owner/repo", pr_number=1, github_token="token"
        )

    def test_format_as_markdown(self):
        result = "This is a test result"
        expected_output = "## Code Security Analysis Results\nThis is a test result"
        self.assertEqual(format_as_markdown(result), expected_output)


if __name__ == "__main__":
    unittest.main()
