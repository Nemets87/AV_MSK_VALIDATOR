r"""
AV MSK Validator — валидатор целостности XML-фида и изображений.

Публичный API:
    from av_msk_validator import validate, ValidationResult
"""

from .validator import ValidationResult, validate

__version__ = "1.0.0"  # было 0.1.0
__all__ = ["ValidationResult", "__version__", "validate"]
