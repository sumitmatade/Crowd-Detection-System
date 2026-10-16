from crowd_detection.cli import main


def test_bad_source_returns_error_code(capsys):
    code = main(["--source", "definitely_missing_file.mp4", "--no-window"])
    assert code == 1
    assert "Could not open" in capsys.readouterr().err
