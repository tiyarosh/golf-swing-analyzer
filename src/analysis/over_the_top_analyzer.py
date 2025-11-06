"""
Over the Top Analyzer (OTT) Module
...docstring...
"""

# Imports
import numpy as np
from typing import Dict, List, Tuple
from ..utils.signal_processing import moving_average, interpolate_nans

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
            "ott_score": 0.0,
            "lateral_movement": 0.0,
            "movement_direction": "insufficient_data",
            "confidence": 0.0,
            "details": {}
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
    
    # Direction depends on golfer handedness and camera angle
    # Assuming face-on view with golfer on right side of frame:
    # - Right-handed golfer: target is to the left
    # - OTT = hands move LEFT (decreasing X) more than expected
    # - Proper = hands stay relatively stable or move RIGHT slightly
    
    # For right-handed golfer facing right side of frame:
    # Negative shift = moving toward target (bad)
    # Positive shift = moving away from target (good)
    
    if golfer_side == "right":
        # More negative = more OTT
        if lateral_shift < -0.05:  # Significant outward movement
            ott_indicator = abs(lateral_shift)
            direction = "outward"
        elif lateral_shift < 0:
            ott_indicator = abs(lateral_shift) * 0.5
            direction = "slight_outward"
        else:
            ott_indicator = 0.0
            direction = "inward"
    else:  # left-handed
        # Opposite for lefties
        if lateral_shift > 0.05:
            ott_indicator = abs(lateral_shift)
            direction = "outward"
        elif lateral_shift > 0:
            ott_indicator = abs(lateral_shift) * 0.5
            direction = "slight_outward"
        else:
            ott_indicator = 0.0
            direction = "inward"
    
    # Convert to 0-10 score
    # Typical OTT might move 5-15% of frame width
    ott_score = min(10.0, ott_indicator * 50)  # Scale to 0-10
    
    # Calculate confidence based on data quality
    # More frames = higher confidence
    # Less variance = higher confidence
    confidence = min(1.0, len(xs) / 30.0)  # Max confidence at 30+ frames
    variance_penalty = min(0.5, np.std(xs_norm) * 2)
    confidence = max(0.1, confidence - variance_penalty)
    
    # Additional metrics
    details = {
        "top_x_position": float(top_x),
        "impact_x_position": float(impact_x),
        "lateral_shift_pixels": float(lateral_shift * video_width),
        "lateral_shift_normalized": float(lateral_shift),
        "path_variance": float(np.std(xs_norm)),
        "frames_analyzed": len(xs)
    }
    
    return {
        "ott_score": float(ott_score),
        "lateral_movement": float(abs(lateral_shift * video_width)),
        "movement_direction": direction,
        "confidence": float(confidence),
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