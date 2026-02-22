from pychorq.cli import main


def test_cli_prints_message(capsys) -> None:
    main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, world from pychorq!"
