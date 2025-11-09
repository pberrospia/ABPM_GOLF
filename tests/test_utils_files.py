import pytest

from app.utils.files import sanitize_upload_filename


@pytest.mark.parametrize(
    "input_name, expected",
    [
        ("../etc/passwd", "passwd"),
        ("..\\evil\\payload.pdf", "payload.pdf"),
        ("   final-report .pdf   ", "final-report_.pdf"),
        ("....hidden", "hidden"),
        ("name with spaces.txt", "name_with_spaces.txt"),
        ("中文文件名.pdf", "_____.pdf"),
    ],
)
def test_sanitize_upload_filename_returns_safe_name(input_name, expected):
    assert sanitize_upload_filename(input_name, fallback="fallback.txt") == expected


def test_sanitize_upload_filename_fallback_when_empty():
    assert sanitize_upload_filename(" ", fallback="fallback.txt") == "fallback.txt"
    assert sanitize_upload_filename(None, fallback="fallback.txt") == "fallback.txt"


def test_sanitize_upload_filename_truncates_long_names():
    long_name = "a" * 300 + ".txt"
    result = sanitize_upload_filename(long_name, fallback="fallback.txt")
    assert len(result) == 255
    assert result.endswith(".txt")
