# Changelog

Все заметные изменения в этом проекте документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [Unreleased]

## [1.0.0] - 2026-11-16

### Added
- Ядро валидатора: проверка XML-фида и целостности связей «запись → изображение».
- CLI-интерфейс: команда `av-msk-validate` с параметрами `--feed`, `--images`, `--strict`.
- Публичное API: `from av_msk_validator import validate, ValidationResult`.
- 11 тестов (unit + CLI), покрытие 93%.
- GitHub Actions CI: lint (ruff) + tests на Python 3.10/3.11/3.12 + сборка пакета.
- GitHub Actions Release: публикация при пуше semver-тега.
- Composite Action `action.yml` для использования в CI других проектов.
- Документация в README.

### Changed
- Версия зафиксирована на `ruff==0.17.5` для воспроизводимости.
- Явный `select` в `[tool.ruff.lint]`: `["E", "F", "I", "UP", "RUF"]`.

[Unreleased]: https://github.com/Nemets87/AV_MSK_VALIDATOR/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Nemets87/AV_MSK_VALIDATOR/releases/tag/v1.0.0
