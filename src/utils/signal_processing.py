"""
Signal Processing Utilities

This module provides utility functions for basic signal processing tasks, including:

- moving_average: Computes a simple centered moving average with edge handling.
- interpolate_nans: Performs linear interpolation to fill NaN values, with forward/back filling at the edges.
- find_flat_window: Scans backward to find a plateau (flat window) in a signal before a given index, based on standard deviation criteria.

Dependencies:
    - numpy

Functions:
    moving_average(x: np.ndarray, w: int) -> np.ndarray
        Computes a centered moving average of the input array with window size w.

    interpolate_nans(y: np.ndarray) -> np.ndarray
        Interpolates NaN values in the input array using linear interpolation, with edge values filled.

    find_flat_window(y, end_idx, max_window=60, min_len=10, max_std=1.0)
        Finds the start and end indices of a flat window (low standard deviation) before a specified end index.

"""

# Imports
import numpy as np
from typing import Tuple, Dict


def moving_average(x: np.ndarray, w: int) -> np.ndarray:
    """Simple centered moving average with edge handling."""
    if w <= 1:
        return x.copy()
    pad = w // 2
    xp = np.pad(x, (pad, pad), mode='edge')
    kernel = np.ones(w, dtype=float) / w
    y = np.convolve(xp, kernel, mode='valid')
    return y

def interpolate_nans(y: np.ndarray) -> np.ndarray:
    """Linear interpolation for NaNs; edges are forward/back filled."""
    yy = y.copy().astype(float)
    n = len(yy)
    isn = np.isnan(yy)
    if not isn.any():
        return yy
    idx = np.arange(n)
    if np.all(isn):
        return np.zeros_like(yy)
    first = np.where(~isn)[0][0]
    last = np.where(~isn)[0][-1]
    yy[:first] = yy[first]
    yy[last+1:] = yy[last]
    isn = np.isnan(yy)
    yy[isn] = np.interp(idx[isn], idx[~isn], yy[~isn])
    return yy

def find_flat_window(y, end_idx, max_window=60, min_len=10, max_std=1.0):
    """Backward scan for a plateau before end_idx with low std."""
    j = end_idx - 1
    best = (None, None)
    while j > 0 and end_idx - j <= max_window:
        seg = y[j:end_idx]
        if len(seg) >= min_len and np.std(seg) <= max_std:
            best = (j, end_idx)
        j -= 1
    return best