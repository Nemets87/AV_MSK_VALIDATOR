r"""
Тесты на CLI (main).

Проверяют:
1. Успешная валидация → main возвращает 0
2. Ошибка валидации → main возвращает 1
3. Флаг --strict превращает предупреждения в ошибку
"""

from __future__ import annotations

from pathlib import Path

from av_msk_validator.cli import main


def test_cli_success(make_feed, make_images, capsys) -> None:
    """Валидные данные → exit code 0."""
    feed = make_feed("<root><item><image>a.jpg</image></item></root>")
    images = make_images(["a.jpg"])

    exit_code = main(["--feed", str(feed), "--images", str(images)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "успешно" in captured.out


def test_cli_failure_missing_image(make_feed, make_images, capsys) -> None:
    """Картинка отсутствует → exit code 1."""
    feed = make_feed("<root><item><image>missing.jpg</image></item></root>")
    images = make_images([])

    exit_code = main(["--feed", str(feed), "--images", str(images)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "ошибками" in captured.out


def test_cli_strict_mode(make_feed, make_images, capsys) -> None:
    """С флагом --strict сиротская картинка становится ошибкой (exit 1)."""
    feed = make_feed("<root><item><image>a.jpg</image></item></root>")
    images = make_images(["a.jpg", "orphan.png"])

    exit_code = main([
        "--feed", str(feed), "--images", str(images), "--strict",
    ])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "strict" in captured.out.lower() or "ошибками" in captured.out


def test_cli_default_arguments(tmp_path: Path, monkeypatch, capsys) -> None:
    """Если аргументы не переданы — используются defaults feed.xml/public_images."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "feed.xml").write_text("<root/>", encoding="utf-8")
    (tmp_path / "public_images").mkdir()

    exit_code = main([])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "успешно" in captured.out