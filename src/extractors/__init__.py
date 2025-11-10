"""Módulo de extratores de dados por fornecedor."""

from src.extractors.gramore_extractor import GramoreExtractor
from src.extractors.elmar_extractor import ElmarExtractor
from src.extractors.rmoura_extractor import RMouraExtractor

__all__ = ["GramoreExtractor", "ElmarExtractor", "RMouraExtractor"]
