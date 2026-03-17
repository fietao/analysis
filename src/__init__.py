"""
Jarvis Stock Analysis Platform
Template-driven valuation engine with support for multiple analysis styles.
"""

__version__ = "2.0.0"
__author__ = "JET / Damodaran Framework"

from .config import DEV_MODE, FINNHUB_API_KEY
from .core.calculator import CalculationEngine, CalculationResult
from .templates.engine import TemplateRegistry, TemplateRenderer

__all__ = [
    'DEV_MODE',
    'FINNHUB_API_KEY',
    'CalculationEngine',
    'CalculationResult',
    'TemplateRegistry',
    'TemplateRenderer',
]
