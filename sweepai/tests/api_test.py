import unittest
from unittest.mock import MagicMock, patch

from sweepai.api import handle_event


class TestHandleEvent(unittest.TestCase):
    def test_handle_event_disabled_repo(self):
        request_dict = {"repository": {"full_name": "sweepai/disabled_repo"}}
        event = "check_run"
        expected_response = {"success": False, "error_message": "Repo is disabled"}
        response = handle_event(request_dict, event)
        self.assertEqual(response, expected_response)

    @patch("sweepai.api.get_github_client")
    @patch("sweepai.api.logger")
    def test_handle_event_check_run_completed(self, mock_logger, mock_get_github_client):
        mock_client = MagicMock()
        mock_repo = MagicMock()
        mock_pull = MagicMock()
        mock_get_github_client.return_value = (None, mock_client)
        mock_client.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pull
        mock_pull.created_at.timestamp.return_value = 100
        request_dict = {"action": "completed", "repository": {"full_name": "sweepai/test_repo"}, "installation": {"id": 1}, "check_run": {"pull_requests": [{"number": 1}]}}
        event = "check_run"
        response = handle_event(request_dict, event)
        mock_get_github_client.assert_called_once()
        mock_repo.get_pull.assert_called_once_with(1)
        self.assertIn("success", response)

    @patch("sweepai.api.get_rules")
    @patch("sweepai.api.logger")
    def test_handle_event_pull_request_opened(self, mock_logger, mock_get_rules):
        mock_get_rules.return_value = ["rule1", "rule2"]
        request_dict = {"action": "opened", "repository": {"full_name": "sweepai/test_repo"}, "pull_request": {"number": 1}}
        event = "pull_request"
        response = handle_event(request_dict, event)
        mock_get_rules.assert_called_once()
        self.assertIn("success", response)

    @patch("sweepai.api.get_github_client")
    @patch("sweepai.api.logger")
    def test_handle_event_error_cases(self, mock_logger, mock_get_github_client):
        mock_get_github_client.side_effect = Exception("GitHub API error")
        request_dict = {"action": "completed", "repository": {"full_name": "sweepai/test_repo"}, "installation": {"id": 1}, "check_run": {"pull_requests": [{"number": 1}]}}
        event = "check_run"
        with self.assertRaises(Exception):
            handle_event(request_dict, event)
        mock_get_github_client.assert_called_once()

if __name__ == '__main__':
    unittest.main()
