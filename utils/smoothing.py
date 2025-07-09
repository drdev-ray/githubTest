"""Smoothing helper functions."""
# TODO: add unit tests

from __future__ import annotations


def ema(prev: float, current: float, alpha: float = 0.35) -> float:
    """Exponential moving average. # TODO: unit test"""
    return alpha * current + (1 - alpha) * prev
