"""Pure geometry, cost, unit conversion, and instructional force calculations."""

from math import pi
from typing import Iterable

import numpy as np

PIXELS_PER_FOOT = 20.0
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 500
TABLE_TOP_Y = 460
MINIMUM_FEET = 1.0
EARTH_GRAVITY_FTPS2 = 32.2
GRAVITY_MODES = {
    "Earth": EARTH_GRAVITY_FTPS2,
    "Mars": 12.21,
    "Moon": 5.33,
}


def px_to_ft(value: float) -> float:
    return value / PIXELS_PER_FOOT


def ft_to_px(value: float) -> float:
    return value * PIXELS_PER_FOOT


def snap(value: float) -> float:
    return round(value / PIXELS_PER_FOOT) * PIXELS_PER_FOOT


def point_in_canvas(x: float, y: float) -> bool:
    return 0 <= x <= CANVAS_WIDTH and 0 <= y <= TABLE_TOP_Y


def snap_point(x: float, y: float) -> tuple[float, float]:
    return snap(x), snap(y)


def segment_length(x1: float, y1: float, x2: float, y2: float) -> float:
    dx = px_to_ft(x2 - x1)
    dy = px_to_ft(y2 - y1)
    return float(np.hypot(dx, dy))


def member_cost(kind: str, length_ft: float) -> float:
    rates = {"column": 90.0, "beam": 70.0, "brace": 40.0}
    return rates[kind] * length_ft


def total_member_cost(members: Iterable) -> float:
    total = 0.0
    for member in members:
        total += member_cost(member.kind, segment_length(*member.endpoints))
    return total


def peak_acceleration_g(amplitude_in: float, frequency_hz: float) -> float:
    amplitude_ft = amplitude_in / 12.0
    acceleration_ftps2 = amplitude_ft * (2 * pi * frequency_hz) ** 2
    return acceleration_ftps2 / EARTH_GRAVITY_FTPS2


def table_motion(elapsed: float, amplitude_in: float, frequency_hz: float) -> tuple[float, float]:
    amplitude_ft = amplitude_in / 12.0
    omega = 2 * pi * frequency_hz
    displacement_ft = amplitude_ft * np.sin(omega * elapsed)
    velocity_ftps = amplitude_ft * omega * np.cos(omega * elapsed)
    return ft_to_px(float(displacement_ft)), float(velocity_ftps)


def table_acceleration(elapsed: float, amplitude_in: float, frequency_hz: float) -> float:
    amplitude_ft = amplitude_in / 12.0
    omega = 2 * pi * frequency_hz
    return float(amplitude_ft * omega * omega * np.sin(omega * elapsed))
