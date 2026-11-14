r"""
AV MSK Validator — валидатор целостности XML-фида и изображений.

Публичный API:
    from av_msk_validator import validate, ValidationResult
"""

from .validator import ValidationResult, validate

__version__ = "0.1.0"
__all__ = ["validate", "ValidationResult", "__version__"]