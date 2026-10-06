"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Call before changing unfamiliar code or data; inspect the instructions and relevant files, then report constraints and likely causes without editing.",
            "system_prompt": "Inspect the requested workspace and report relevant instructions, file paths, evidence, and likely causes. Do not modify files. Be concise and distinguish observed facts from guesses.",
        },
        {
            "name": "implementer",
            "description": "Call when a task needs a focused code or data change; implement only the requested change and run the most relevant checks.",
            "system_prompt": "Make the requested change in the workspace. Read relevant instructions before editing, preserve existing conventions, and run the relevant tests or validation. Report changed files and exact check results.",
        },
        {
            "name": "reviewer",
            "description": "Call after a change when an independent check of requirements, edge cases, or generated output would reduce risk.",
            "system_prompt": "Review the current workspace against the task instructions. Check relevant tests and edge cases without modifying files. Report concrete issues with file paths and evidence; say when no issue is found.",
        },
    ]
