import os
import subprocess
import unittest
from unittest.mock import MagicMock, mock_open, patch

from guard.scanner import (
    fetch_changed_files_from_pr,
    fetch_changed_files_from_repo,
    generate_code_summary,
    get_changed_files,
    get_pr_changed_files,
    is_git_repo,
    read_files_and_generate_summary,
    scan_changes,
    scan_files,
)


class TestScanner(unittest.TestCase):
    @patch("subprocess.check_output")
    def test_is_git_repo_valid(self, mock_check_output):
        mock_check_output.return_value = b"true\n"
        self.assertTrue(is_git_repo(os.path.join("some", "valid", "repo")))

    @patch(
        "subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "git")
    )
    def test_is_git_repo_invalid(self, mock_check_output):
        self.assertFalse(is_git_repo(os.path.join("some", "invalid", "repo")))

    @patch("guard.scanner.Github")
    def test_get_pr_changed_files(self, mock_github):
        mock_pr = MagicMock()
        mock_pr.get_files.return_value = [
            MagicMock(filename="file1.py"),
            MagicMock(filename="file2.py"),
        ]
        mock_repo = MagicMock()
        mock_repo.get_pull.return_value = mock_pr
        mock_github.return_value.get_repo.return_value = mock_repo

        files = get_pr_changed_files("some/repo", 1, "fake_token")
        self.assertEqual(files, ["file1.py", "file2.py"])

    @patch("os.walk")
    @patch("builtins.open", new_callable=mock_open, read_data="sample code")
    def test_scan_files(self, mock_open, mock_walk):
        mock_walk.return_value = [
            (os.path.join("some", "dir"), ("subdir",), ("file1.py", "file2.py")),
        ]
        mock_ai_client = MagicMock()
        mock_ai_client.scan_code.return_value = "Scan result"

        result = scan_files(os.path.join("some", "dir"), mock_ai_client)
        self.assertIn("Scan result", result)
        mock_ai_client.scan_code.assert_called_once()

    @patch("subprocess.check_output")
    @patch("os.chdir")
    def test_get_changed_files(self, mock_chdir, mock_check_output):
        mock_check_output.return_value = "file1.py\nfile2.py\n"
        files = get_changed_files(os.path.join("some", "repo"))
        self.assertEqual(files, ["file1.py", "file2.py"])
        mock_chdir.assert_called_once_with(os.path.join("some", "repo"))

    @patch("guard.scanner.get_pr_changed_files")
    def test_fetch_changed_files_from_pr(self, mock_get_pr_changed_files):
        mock_get_pr_changed_files.return_value = ["file1.py", "file2.py"]
        files = fetch_changed_files_from_pr("some/repo", 1, "fake_token")
        self.assertEqual(files, ["file1.py", "file2.py"])

    @patch("builtins.open", new_callable=mock_open, read_data="sample code")
    @patch("os.path.isfile", return_value=True)
    def test_read_files_and_generate_summary(self, mock_isfile, mock_open):
        file_paths = [
            os.path.join("some", "repo", "file1.py"),
            os.path.join("some", "repo", "file2.py"),
        ]

        code_summary = read_files_and_generate_summary(file_paths)

        self.assertIn("File: file1.py", code_summary)
        self.assertIn("sample code", code_summary)
        self.assertIn("File: file2.py", code_summary)

        mock_open.assert_any_call(
            os.path.join("some", "repo", "file1.py"), "r", encoding="utf-8"
        )
        mock_open.assert_any_call(
            os.path.join("some", "repo", "file2.py"), "r", encoding="utf-8"
        )

    @patch("builtins.open", new_callable=mock_open, read_data="sample code")
    @patch("os.path.isfile", return_value=False)
    def test_read_files_and_generate_summary_invalid_file(self, mock_isfile, mock_open):
        file_paths = [os.path.join("some", "repo", "invalid_file.py")]

        code_summary = read_files_and_generate_summary(file_paths)

        self.assertEqual(code_summary, "")
        mock_open.assert_not_called()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.isfile", return_value=True)
    def test_read_files_and_generate_summary_decoding_error(
        self, mock_isfile, mock_open
    ):
        mock_open.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "decoding error")
        file_paths = [os.path.join("some", "repo", "file1.py")]

        code_summary = read_files_and_generate_summary(file_paths)

        self.assertEqual(code_summary, "")
        mock_open.assert_called_once_with(
            os.path.join("some", "repo", "file1.py"), "r", encoding="utf-8"
        )

    @patch("guard.scanner.is_git_repo", return_value=False)
    def test_fetch_changed_files_from_repo_invalid(self, mock_is_git_repo):
        with self.assertRaises(ValueError):
            fetch_changed_files_from_repo(os.path.join("invalid", "repo"))

    @patch("guard.scanner.is_git_repo", return_value=True)
    @patch("guard.scanner.get_changed_files", return_value=["file1.py", "file2.py"])
    def test_fetch_changed_files_from_repo_valid(
        self, mock_get_changed_files, mock_is_git_repo
    ):
        files = fetch_changed_files_from_repo(os.path.join("valid", "repo"))
        self.assertEqual(files, ["file1.py", "file2.py"])

    @patch("builtins.open", new_callable=mock_open, read_data="sample code")
    @patch("os.path.isfile", return_value=True)
    def test_generate_code_summary(self, mock_isfile, mock_open):
        changed_files = ["file1.py", "file2.py"]

        code_summary = generate_code_summary(
            os.path.join("some", "repo"), changed_files
        )
        self.assertIn("sample code", code_summary)

        mock_open.assert_any_call(
            os.path.join("some", "repo", "file1.py"), "r", encoding="utf-8"
        )
        mock_open.assert_any_call(
            os.path.join("some", "repo", "file2.py"), "r", encoding="utf-8"
        )

    @patch("guard.scanner.fetch_changed_files_from_pr")
    @patch("guard.scanner.generate_code_summary")
    def test_scan_changes_with_pr(
        self, mock_generate_code_summary, mock_fetch_changed_files_from_pr
    ):
        mock_generate_code_summary.return_value = "code summary"
        mock_fetch_changed_files_from_pr.return_value = ["file1.py"]

        mock_ai_client = MagicMock()
        mock_ai_client.scan_code.return_value = "Scan result"

        result = scan_changes(
            os.path.join("some", "repo"),
            mock_ai_client,
            repo="some/repo",
            pr_number=1,
            github_token="fake_token",
        )
        self.assertIn("Scan result", result)

    @patch("guard.scanner.fetch_changed_files_from_repo")
    @patch("guard.scanner.generate_code_summary")
    def test_scan_changes_with_local_repo(
        self, mock_generate_code_summary, mock_fetch_changed_files_from_repo
    ):
        mock_generate_code_summary.return_value = "code summary"
        mock_fetch_changed_files_from_repo.return_value = ["file1.py"]

        mock_ai_client = MagicMock()
        mock_ai_client.scan_code.return_value = "Scan result"

        result = scan_changes(os.path.join("some", "repo"), mock_ai_client)
        self.assertIn("Scan result", result)


if __name__ == "__main__":
    unittest.main()
