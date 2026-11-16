r"""
Общие фикстуры для тестов валидатора.

Фикстуры pytest — это функции, которые готовят данные для тестов.
Они переиспользуются: создаём временный фид и папку с картинками один раз,
а pytest подставляет их в тесты по имени аргумента.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

# Тип-алиас для фабрики фидов: вызываешь — получаешь Path к созданному файлу
FeedFactory = Callable[..., Path]
ImagesFactory = Callable[..., Path]


@pytest.fixture
def make_feed(tmp_path: Path) -> FeedFactory:
    """
    Фабрика временных фидов.

    Использование:
        feed = make_feed('<root><item><image>a.jpg</image></item></root>')
        feed = make_feed('не битый XML')       # битый XML
        feed = make_feed('')                    # пустой файл
        feed = make_feed(None)                  # файл вообще не создаётся

    Возвращает путь к файлу feed.xml во временной папке.
    """
    counter = {"n": 0}

    def _factory(content: str | None = "<root/>") -> Path:
        counter["n"] += 1
        feed_path = tmp_path / f"feed_{counter['n']}.xml"
        if content is not None:
            feed_path.write_text(content, encoding="utf-8")
        # Если content=None — файл не создаём, тест проверит «файл не найден»
        return feed_path

    return _factory


@pytest.fixture
def make_images(tmp_path: Path) -> ImagesFactory:
    """
    Фабрика временных папок с «изображениями».

    Использование:
        images_dir = make_images(["a.jpg", "b.png"])
        images_dir = make_images([])                     # пустая папка
        images_dir = make_images(None)                   # папка не создаётся

    Возвращает путь к папке с файлами-пустышками нужных расширений.
    """
    counter = {"n": 0}

    def _factory(filenames: list[str] | None = None) -> Path:
        counter["n"] += 1
        images_dir = tmp_path / f"images_{counter['n']}"
        if filenames is not None:
            images_dir.mkdir(parents=True, exist_ok=True)
            for name in filenames:
                (images_dir / name).write_bytes(b"")  # содержимое не важно
        return images_dir

    return _factory