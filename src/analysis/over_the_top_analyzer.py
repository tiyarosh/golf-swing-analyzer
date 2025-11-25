"""
Over the Top Analyzer (OTT) Module

This module provides functions to analyze golf swing data for "over-the-top" (OTT) swing characteristics.
It includes methods to extract hand path coordinates, analyze lateral hand movement for OTT tendencies,
evaluate shoulder rotation patterns, and generate human-readable reports summarizing OTT analysis.
Functions:
    - extract_hand_path(xs, ys, phase_ranges, phases_to_track): 
        Extracts and processes hand path coordinates during specified swing phases, interpolating and smoothing data as needed.
    - analyze_ott_deviation(hand_path, video_width, golfer_side):
        Analyzes the hand path for OTT characteristics by quantifying lateral movement and direction, returning a severity score and confidence.
    - analyze_shoulder_rotation(shoulder_data, video_width):
        Evaluates shoulder rotation patterns for OTT indicators, such as early or excessive rotation, and returns rotation metrics and confidence.
    - generate_ott_report(hand_analysis, shoulder_analysis):
        Generates a formatted, human-readable report summarizing the OTT analysis results for both hand path and shoulder rotation.
Dependencies:
    - numpy
    - typing
    - signal processing utilities: moving_average, interpolate_nans
"""

# Imports
import numpy as np
from typing import Dict, List, Tuple
from ..utils.signal_processing import moving_average, interpolate_nans

# Benchmark constants (based on typical golf instruction standards)
BENCHMARKS = {
    "optimal_path_degrees": (-4, 4),  # Optimal swing path: slight in-to-out to square
    "tour_avg_path": 1.5,  # Tour average: 1-2° in-to-out
    "optimal_rotation_rate": (1.0, 2.5),  # Degrees per frame
    "tour_avg_rotation_rate": 1.8,
    "severe_ott_threshold": 5.0,  # 5°+ out-to-in is severe OTT
}

def extract_hand_path(xs: np.ndarray, ys: np.ndarray, 
                      phase_ranges: dict, 
                      phases_to_track: list = ["Top", "Downswing", "Impact"]):
    """
    Extract hand path coordinates during specified phases.
    Interpolates missing values for smooth path.
    
    Args:
        xs, ys: wrist position arrays (may contain NaNs)
        phase_ranges: dict from detect_swing_phases
        phases_to_track: which phases to include in path
        
    Returns:
        dict with:
            - frame_idxs: frame numbers along path
            - xs: interpolated X positions
            - ys: interpolated Y positions
            - start_frame, end_frame: path boundaries
    """
    # Determine frame range
    start_frame = min(phase_ranges[p][0] for p in phases_to_track if p in phase_ranges)
    end_frame = max(phase_ranges[p][1] for p in phases_to_track if p in phase_ranges)
    
    # Extract segment
    seg_xs = xs[start_frame:end_frame+1].copy()
    seg_ys = ys[start_frame:end_frame+1].copy()
    
    # Interpolate any NaNs
    seg_xs = interpolate_nans(seg_xs)
    seg_ys = interpolate_nans(seg_ys)
    
    # Smooth for cleaner path
    seg_xs = moving_average(seg_xs, 5)
    seg_ys = moving_average(seg_ys, 5)
    
    frame_idxs = np.arange(start_frame, end_frame + 1)
    
    return {
        "frame_idxs": frame_idxs,
        "xs": seg_xs,
        "ys": seg_ys,
        "start_frame": start_frame,
        "end_frame": end_frame
    }

def analyze_ott_deviation(hand_path: dict, 
                          video_width: int,
                          golfer_side: str = "right"):
    """
    Analyze hand path for over-the-top characteristics.
    
    Key insight: OTT means hands move OUTWARD toward target line
    during downswing instead of dropping "into the slot".
    
    Args:
        hand_path: dict from extract_hand_path()
        video_width: video width in pixels
        golfer_side: "right" or "left" handed
        
    Returns:
        dict with:
            - ott_score: 0-10 (0=perfect, 10=severe OTT)
            - lateral_movement: total lateral shift in pixels
            - movement_direction: "outward" or "inward"
            - confidence: 0-1
            - details: additional metrics
    """
    xs = hand_path["xs"]
    ys = hand_path["ys"]
    frames = hand_path["frame_idxs"]
    
    if len(xs) < 3:
        return {
            "swing_path_degrees": 0.0,
            "swing_path_description": "Insufficient data",
            "lateral_movement_percent": 0.0,
            "vs_tour_average": 0.0,
            "severity_level": "Unable to analyze",
            "data_quality": "Poor - insufficient frames",
            "details": {"frames_analyzed": len(xs)}
        }
    
    # Normalize X to 0-1 scale
    xs_norm = xs / video_width
    
    # Calculate lateral movement from top to impact
    # First 1/3 of path = top area
    # Last 1/3 of path = impact area
    n = len(xs_norm)
    top_third = xs_norm[:max(1, n//3)]
    impact_third = xs_norm[max(1, -n//3):]
    
    top_x = np.mean(top_third)
    impact_x = np.mean(impact_third)
    
    # Lateral shift
    lateral_shift = impact_x - top_x
    lateral_percent = lateral_shift * 100

    PIXELS_TO_DEGREES_FACTOR = 1.8
    
    # Direction depends on golfer handedness and camera angle
    # Assuming face-on view with golfer on right side of frame:
    # - Right-handed golfer: target is to the left
    # - OTT = hands move LEFT (decreasing X) more than expected
    # - Proper = hands stay relatively stable or move RIGHT slightly
    
    # For right-handed golfer facing right side of frame:
    # Negative shift = moving toward target (bad)
    # Positive shift = moving away from target (good)
    
    if golfer_side == "right":
        # Right-handed golfer facing right side of frame:
        # Moving left (negative shift) = out-to-in (OTT)
        # Moving right (positive shift) = in-to-out (good)
        swing_path_degrees = -lateral_percent * PIXELS_TO_DEGREES_FACTOR
    else:  # left-handed
        # Opposite for lefties
        swing_path_degrees = lateral_percent * PIXELS_TO_DEGREES_FACTOR
    
    # Generate standard golf terminology description
    abs_degrees = abs(swing_path_degrees)
    if swing_path_degrees < -1.0:
        path_description = f"{abs_degrees:.1f}° out-to-in"
    elif swing_path_degrees > 1.0:
        path_description = f"{abs_degrees:.1f}° in-to-out"
    else:
        path_description = f"{abs_degrees:.1f}° (nearly square)"
    
    # Compare to tour average
    vs_tour = swing_path_degrees - BENCHMARKS["tour_avg_path"]
    
    # Determine severity level with clear descriptions
    if swing_path_degrees >= BENCHMARKS["optimal_path_degrees"][0] and \
       swing_path_degrees <= BENCHMARKS["optimal_path_degrees"][1]:
        severity = "Optimal - Excellent swing path"
    elif swing_path_degrees > -5.0 and swing_path_degrees < BENCHMARKS["optimal_path_degrees"][0]:
        severity = "Mild OTT - Slight out-to-in path"
    elif swing_path_degrees <= -BENCHMARKS["severe_ott_threshold"]:
        severity = "Severe OTT - Significant out-to-in path"
    elif swing_path_degrees < -5.0:
        severity = "Moderate OTT - Noticeable out-to-in path"
    elif swing_path_degrees > BENCHMARKS["optimal_path_degrees"][1]:
        severity = "Strong in-to-out path (may cause hooks)"
    else:
        severity = "Good - Within acceptable range"
    
    # Calculate data quality based on frames and consistency
    frames_quality = min(100, (len(xs) / 30.0) * 100)  # 30+ frames = 100%
    consistency = 100 - min(100, np.std(xs_norm) * 200)  # Lower variance = better
    overall_quality = (frames_quality * 0.7 + consistency * 0.3)
    
    if overall_quality >= 80:
        quality_desc = f"Excellent ({len(xs)} frames analyzed)"
    elif overall_quality >= 60:
        quality_desc = f"Good ({len(xs)} frames analyzed)"
    elif overall_quality >= 40:
        quality_desc = f"Fair ({len(xs)} frames, some inconsistency)"
    else:
        quality_desc = f"Poor ({len(xs)} frames, high variance)"
    
    # Additional metrics for debugging/advanced users
    details = {
        "top_x_position": float(top_x),
        "impact_x_position": float(impact_x),
        "lateral_shift_percent": float(lateral_percent),
        "path_variance": float(np.std(xs_norm)),
        "frames_analyzed": len(xs),
        "quality_score": float(overall_quality)
    }
    
    return {
        "swing_path_degrees": float(swing_path_degrees),
        "swing_path_description": path_description,
        "lateral_movement_percent": float(abs(lateral_percent)),
        "vs_tour_average": float(vs_tour),
        "severity_level": severity,
        "data_quality": quality_desc,
        "details": details
    }

def analyze_shoulder_rotation(shoulder_data: dict, video_width: int):
    """
    Analyze shoulder rotation pattern for OTT indicators.
    
    OTT characteristic: Shoulders rotate EARLY and OUTWARD
    (spinning toward target instead of turning through)
    
    Returns:
        dict with rotation metrics
    """
    if len(shoulder_data) < 3:
        return {
            "rotation_score": 0.0,
            "rotation_rate": 0.0,
            "early_rotation": False,
            "confidence": 0.0
        }
    
    frames = sorted(shoulder_data.keys())
    
    # Calculate shoulder line angles over time
    angles = []
    for frame in frames:
        left_x, left_y, _ = shoulder_data[frame]['left']
        right_x, right_y, _ = shoulder_data[frame]['right']
        
        # Angle of shoulder line
        dx = right_x - left_x
        dy = right_y - left_y
        angle = np.arctan2(dy, dx) * 180 / np.pi
        angles.append(angle)
    
    angles = np.array(angles)
    
    # Calculate rotation rate (degrees per frame)
    rotation_rates = np.diff(angles)
    avg_rotation_rate = np.mean(np.abs(rotation_rates))
    
    # High rotation rate in early downswing = OTT indicator
    # Proper swing: shoulders rotate more gradually
    early_rotation = avg_rotation_rate > 2.0  # >2 deg/frame is fast
    
    # Score based on rotation rate
    rotation_score = min(10.0, avg_rotation_rate * 2.0)
    
    confidence = min(1.0, len(frames) / 15.0)
    
    return {
        "rotation_score": float(rotation_score),
        "rotation_rate": float(avg_rotation_rate),
        "early_rotation": bool(early_rotation),
        "confidence": float(confidence),
        "angles": angles.tolist(),
        "frames": frames
    }

def generate_ott_report(
    hand_analysis: Dict,
    shoulder_analysis: Dict = None
) -> str:
    """
    Generate a human-readable OTT analysis report.
    
    Args:
        hand_analysis: Result from analyze_ott_deviation()
        shoulder_analysis: Optional result from analyze_shoulder_rotation()
        
    Returns:
        Formatted string report
    """
    report = []
    report.append("="*60)
    report.append("OVER-THE-TOP (OTT) ANALYSIS REPORT")
    report.append("="*60)
    
    # Hand path analysis
    report.append("\n📊 HAND PATH ANALYSIS")
    report.append(f"  OTT Score: {hand_analysis['ott_score']:.1f}/10")
    report.append(f"  Direction: {hand_analysis['movement_direction'].replace('_', ' ').title()}")
    report.append(f"  Lateral Movement: {hand_analysis['lateral_movement']:.1f} pixels")
    report.append(f"  Confidence: {hand_analysis['confidence']*100:.0f}%")
    
    # Interpretation
    if hand_analysis['ott_score'] < 2.0:
        severity = "Excellent - No significant OTT tendency"
    elif hand_analysis['ott_score'] < 4.0:
        severity = "Good - Minor lateral movement detected"
    elif hand_analysis['ott_score'] < 6.0:
        severity = "Moderate - Noticeable OTT pattern"
    elif hand_analysis['ott_score'] < 8.0:
        severity = "Significant - Strong OTT tendency"
    else:
        severity = "Severe - Major OTT issue"
    
    report.append(f"\n  Assessment: {severity}")
    
    # Shoulder analysis if available
    if shoulder_analysis and shoulder_analysis.get('confidence', 0) > 0.3:
        report.append("\n SHOULDER ROTATION ANALYSIS")
        report.append(f"  Rotation Score: {shoulder_analysis['rotation_score']:.1f}/10")
        report.append(f"  Rotation Rate: {shoulder_analysis['rotation_rate']:.2f}°/frame")
        report.append(f"  Early Rotation: {'Yes' if shoulder_analysis['early_rotation'] else 'No'}")
        report.append(f"  Confidence: {shoulder_analysis['confidence']*100:.0f}%")
    
    report.append("\n" + "="*60)
    
    return "\n".join(report)