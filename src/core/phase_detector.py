"""
Phase Detector Module

This module provides functionality to detect phases in a golf swing using wrist-y position data.
It includes the main function `detect_swing_phases` which processes the wrist-y signal, applies smoothing,
calculates velocity, and identifies key swing events such as swing start, top, impact, and swing end.
The function returns a dictionary containing the smoothed signal, velocity, detected swing indices,
and a mapping of swing phase ranges.

Functions:
    detect_swing_phases(wrist_y: np.ndarray,
                        smoothing_window: int = 5,
                        precheck_window: int = 30,
                        threshold_percentile: float = 90.0) -> Dict:
        Detects swing phases from wrist-y position data.
        Args:
            wrist_y (np.ndarray): Array of wrist-y position values (may contain NaNs).
            smoothing_window (int): Window size for moving average smoothing.
            precheck_window (int): Number of frames to skip at the start for threshold calculation.
            threshold_percentile (float): Percentile for velocity threshold to detect swing start.
        Returns:
            Dict: Dictionary containing:
                - "smoothed": Smoothed wrist-y signal.
                - "velocity": Absolute velocity of the smoothed signal.
                - "swing_start": Index of detected swing start.
                - "swing_end": Index of detected swing end.
                - "phase_ranges": Dictionary mapping swing phases to their index ranges.
        Raises:
            ValueError: If there are not enough frames to detect a swing.


"""

# Imports
import numpy as np
from typing import Dict, Tuple
from ..utils.signal_processing import moving_average, interpolate_nans, find_flat_window

def detect_swing_phases(wrist_y: np.ndarray,
                        smoothing_window:int = 5,
                        precheck_window:int = 30,
                        threshold_percentile:float = 90.0) -> Dict:
    """Detect swing phases from wrist-y. Returns dict of results."""
    y = interpolate_nans(wrist_y)
    sm = moving_average(y, smoothing_window)
    vel = np.abs(np.gradient(sm))

    b = min(precheck_window, len(vel)//3)
    b = max(0, b)
    tail = vel[b:]
    if len(tail) == 0:
        raise ValueError("Not enough frames to detect swing.")

    thr = np.percentile(tail, threshold_percentile)
    cand = np.where(vel[b:] > thr)[0]
    swing_start = int(cand[0] + b) if len(cand) else int(np.argmax(vel))

    peak_idx = int(np.argmax(vel[swing_start:]) + swing_start)
    start_y = sm[swing_start]
    if peak_idx + 1 < len(sm):
        post = np.arange(peak_idx + 1, len(sm))
        e_rel = np.argmin(np.abs(sm[post] - start_y))
        swing_end = int(post[e_rel])
    else:
        swing_end = len(sm) - 1

    swing_start = max(0, min(swing_start, len(sm)-1))
    swing_end   = max(swing_start+1, min(swing_end, len(sm)-1))

    seg = sm[swing_start:swing_end+1]
    if len(seg) < 3:
        phase_ranges = {
            "Address": (0, swing_start),
            "Backswing": (swing_start, swing_end),
            "Top": (swing_end, swing_end),
            "Downswing": (swing_end, swing_end),
            "Impact": (swing_end, swing_end),
            "Follow Through": (swing_end, len(sm)-1)
        }
        return {
            "smoothed": sm, "velocity": vel,
            "swing_start": swing_start, "swing_end": swing_end,
            "phase_ranges": phase_ranges
        }

    local_min_rel = int(np.argmin(seg))
    top_idx = swing_start + local_min_rel
    top_l = max(swing_start, top_idx - 5)
    top_r = min(swing_end, top_idx + 5)

    post_top = sm[top_r:swing_end+1]
    if len(post_top) >= 3:
        impact_rel = int(np.argmax(post_top))
        impact_idx = top_r + impact_rel
        local_min = float(np.min(post_top))
        local_max = float(np.max(post_top))
        dynamic_tol = 0.05 * (local_max - local_min + 1e-6)
        L = impact_idx
        R = impact_idx
        while L-1 >= top_r and abs(sm[L-1] - sm[impact_idx]) <= dynamic_tol:
            L -= 1
        while R+1 <= swing_end and abs(sm[R+1] - sm[impact_idx]) <= dynamic_tol:
            R += 1
        impact_l, impact_r = L, R
    else:
        impact_l = impact_r = swing_end

    d0 = top_r
    d1 = max(d0, impact_l)

    addr = find_flat_window(sm, swing_start, max_window=60, min_len=10, max_std=1.0)
    if addr == (None, None):
        a0 = max(0, swing_start - 15)
        a1 = swing_start
    else:
        a0, a1 = addr

    phase_ranges = {
        "Address": (a0, a1),
        "Backswing": (swing_start, top_l),
        "Top": (top_l, top_r),
        "Downswing": (d0, d1),
        "Impact": (impact_l, impact_r),
        "Follow Through": (impact_r, swing_end)
    }
    return {
        "smoothed": sm, "velocity": vel,
        "swing_start": swing_start, "swing_end": swing_end,
        "phase_ranges": phase_ranges
    }