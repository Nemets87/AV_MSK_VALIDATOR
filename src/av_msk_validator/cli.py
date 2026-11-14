r"""
Командная строка валидатора AV_MSK.

Использование:
    av-msk-validate --feed feed.xml --images public_images
    python -m av_msk_validator --feed feed.xml --images public_images
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .validator import validate


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="av-msk-validate",
        description="Валидатор XML-фида и изображений для проекта AV_MSK.",
    )
    parser.add_argument(
        "--feed",
        type=Path,
        default=Path("feed.xml"),
        help="Путь к XML-фиду (по умолчанию: feed.xml)",
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=Path("public_images"),
        help="Путь к папке с изображениями (по умолчанию: public_images)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Считать «сиротские» картинки ошибкой (по умолчанию — только предупреждение)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI. Возвращает код выхода: 0 — успех, 1 — ошибки."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    print(f"🔍 Валидация фида: {args.feed}")
    print(f"🖼️  Папка изображений: {args.images}\n")

    result = validate(args.feed, args.images)

    # Статистика
    stats = result.stats
    if "total_elements" in stats:
        print(f"📊 Всего элементов в XML: {stats['total_elements']:,}")
    if "top_tags" in stats:
        print("   Топ-5 тегов:")
        for tag, count in stats["top_tags"]:
            print(f"   - <{tag}>: {count:,}")
    if "image_refs_in_xml" in stats:
        print(f"\n🖼️  Упоминаний изображений в XML: {stats['image_refs_in_xml']}")
    if "image_files_on_disk" in stats:
        print(f"🖼️  Файлов изображений на диске: {stats['image_files_on_disk']}")

    # Ошибки
    if result.errors:
        print("\n❌ Ошибки:")
        for err in result.errors:
            print(f"   {err}")

    # Предупреждения
    if result.warnings:
        print("\n⚠️  Предупреждения:")
        for warn in result.warnings:
            print(f"   {warn}")

    # Политика --strict: «сиротские» картинки становятся ошибкой
    if args.strict and result.warnings:
        result.ok = False
        print("\n🚨 Режим --strict: предупреждения считаются ошибкой.")

    if result.ok:
        print("\n🎉 Валидация пройдена успешно!")
        return 0
    print("\n💥 Валидация завершена с ошибками.")
    return 1


if __name__ == "__main__":
    sys.exit(main())