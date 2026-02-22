from pychorq.core import get_message


def test_get_message() -> None:
    assert get_message() == "Hello, world from pychorq!"
