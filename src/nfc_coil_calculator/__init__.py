"""Offline calculator for rectangular 13.56 MHz NFC PCB spiral antennas."""

from .coil_engine import CoilResult, CoilSpec, calculate, spiral_points

__version__ = "2.0.0"

__all__ = ["CoilResult", "CoilSpec", "__version__", "calculate", "spiral_points"]
