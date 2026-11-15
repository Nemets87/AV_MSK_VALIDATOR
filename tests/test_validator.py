r"""
Тесты на ядро валидатора (validate).

Покрывают 6 сценариев:
1. Успех: валидный фид + все картинки на месте
2. Файл фида отсутствует
3. Файл фида пустой
4. Фид содержит битый XML
5. Картинка из фида отсутствует на диске (критическая ошибка)
6. «Сиротская» картинка на диске (предупреждение, не ошибка)
"""

from __future__ import annotations

from pathlib import Path

from av_msk_validator import ValidationResult, validate


def test_validation_success(make_feed, make_images) -> None:
    """Валидный фид + все картинки на месте → ok=True, без ошибок."""
    feed = make_feed(
        '<root><item><image>a.jpg</image></item>'
        '<item><image>b.png</image></item></root>'
    )
    images = make_images(["a.jpg", "b.png"])

    result = validate(feed, images)

    assert isinstance(result, ValidationResult)
    assert result.ok is True
    assert result.errors == []
    assert result.warnings == []
    assert result.stats["image_refs_in_xml"] == 2
    assert result.stats["image_files_on_disk"] == 2


def test_validation_feed_missing(make_feed, make_images) -> None:
    """Файла фида нет → ok=False, понятная ошибка."""
    feed = make_feed(None)  # файл не создаётся
    images = make_images([])

    result = validate(feed, images)

    assert result.ok is False
    assert any("не найден" in e for e in result.errors)


def test_validation_feed_empty(make_feed, make_images) -> None:
    """Файл фида пустой → ok=False."""
    feed = make_feed("")  # создаётся, но пустой
    images = make_images([])

    result = validate(feed, images)

    assert result.ok is False
    assert any("пустой" in e for e in result.errors)


def test_validation_broken_xml(make_feed, make_images) -> None:
    """Битый XML → ok=False с упоминанием ошибки парсинга."""
    feed = make_feed("<root><item>")  # незакрытый тег
    images = make_images([])

    result = validate(feed, images)

    assert result.ok is False
    assert any("XML" in e for e in result.errors)


def test_validation_missing_image_on_disk(make_feed, make_images) -> None:
    """XML ссылается на картинку, которой нет на диске → ok=False."""
    feed = make_feed("<root><item><image>missing.jpg</image></item></root>")
    images = make_images([])  # пустая папка — файла нет

    result = validate(feed, images)

    assert result.ok is False
    assert any("отсутствуют на диске" in e for e in result.errors)
    assert any("missing.jpg" in e for e in result.errors)


def test_validation_unused_image_on_disk(make_feed, make_images) -> None:
    """Сиротская картинка на диске → только предупреждение, ok=True."""
    feed = make_feed("<root><item><image>a.jpg</image></item></root>")
    images = make_images(["a.jpg", "orphan.png"])

    result = validate(feed, images)

    assert result.ok is True, "Сиротская картинка — не критическая ошибка"
    assert any("не упомянуты" in w for w in result.warnings)
    assert any("orphan.png" in w for w in result.warnings)


def test_validation_images_dir_missing(make_feed) -> None:
    """Папки с картинками нет → ok=False."""
    feed = make_feed("<root><item><image>a.jpg</image></item></root>")
    missing_dir = Path("/nonexistent/path/to/images")

    result = validate(feed, missing_dir)

    assert result.ok is False
    assert any("не найдена" in e for e in result.errors)