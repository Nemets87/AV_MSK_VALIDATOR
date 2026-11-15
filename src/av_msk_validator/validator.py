r"""
Ядро валидатора AV_MSK.

Проверяет целостность XML-фида и связей «запись → изображение».
Не зависит от конкретных путей — всё передаётся аргументами.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".bmp"}
)


@dataclass
class ValidationResult:
    """Результат валидации: успех/неуспех + человекочитаемые сообщения."""

    ok: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, object] = field(default_factory=dict)


def _is_image_reference(value: str) -> bool:
    value_lower = value.lower()
    return any(ext in value_lower for ext in IMAGE_EXTENSIONS)


def _normalize_path(value: str) -> str:
    return Path(value.strip().split("?")[0]).name


def _collect_image_references(root: ET.Element) -> set[str]:
    refs: set[str] = set()
    for elem in root.iter():
        for attr_value in elem.attrib.values():
            if _is_image_reference(attr_value):
                refs.add(_normalize_path(attr_value))
        if elem.text and _is_image_reference(elem.text):
            refs.add(_normalize_path(elem.text))
    return refs


def validate(feed_path: Path, images_dir: Path) -> ValidationResult:
    """Проверяет фид и папку с изображениями. Возвращает ValidationResult."""
    result = ValidationResult()

    # 1. Фид существует и не пустой
    if not feed_path.exists():
        result.ok = False
        result.errors.append(f"Файл фида не найден: {feed_path}")
        return result
    if feed_path.stat().st_size == 0:
        result.ok = False
        result.errors.append(f"Файл фида пустой: {feed_path}")
        return result

    # 2. XML парсится
    try:
        tree = ET.parse(feed_path)
        root = tree.getroot()
    except ET.ParseError as exc:
        result.ok = False
        result.errors.append(f"Ошибка парсинга XML: {exc}")
        return result

    # 3. Статистика по тегам
    tag_counter = Counter(elem.tag for elem in root.iter())
    result.stats["total_elements"] = sum(tag_counter.values())
    result.stats["top_tags"] = tag_counter.most_common(5)

    # 4. Ссылки на изображения из XML
    xml_refs = _collect_image_references(root)
    result.stats["image_refs_in_xml"] = len(xml_refs)

    # 5. Файлы изображений на диске
    if not images_dir.exists():
        result.ok = False
        result.errors.append(f"Папка с изображениями не найдена: {images_dir}")
        return result

    disk_files = {
        f.name
        for f in images_dir.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    }
    result.stats["image_files_on_disk"] = len(disk_files)

    # 6. Сравнение множеств
    missing_on_disk = xml_refs - disk_files
    unused_on_disk = disk_files - xml_refs

    if missing_on_disk:
        result.ok = False
        result.errors.append(
            f"В XML упомянуты, но отсутствуют на диске: {len(missing_on_disk)}"
        )
        for name in sorted(missing_on_disk)[:10]:
            result.errors.append(f"  - {name}")
        if len(missing_on_disk) > 10:
            result.errors.append(f"  ... и ещё {len(missing_on_disk) - 10}")

    if unused_on_disk:
        result.warnings.append(
            f"На диске есть, но не упомянуты в XML: {len(unused_on_disk)}"
        )
        for name in sorted(unused_on_disk)[:5]:
            result.warnings.append(f"  - {name}")

    return result