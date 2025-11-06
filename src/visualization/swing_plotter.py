"""
Swing Plotting Module
...docstring...
"""

# Imports
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple
from ..utils.signal_processing import interpolate_nans, moving_average

def plot_phases(smoothed: np.ndarray,
                phase_ranges: dict,
                swing_start: int,
                swing_end: int,
                title: str = "Golf Swing Phases (wrist-Y)"):
    """Plot flipped smoothed trajectory with phase bands."""
    x = np.arange(len(smoothed))
    y_plot = -smoothed  # flip so "up" is up

    fig, ax = plt.subplots(figsize=(12, 5), dpi=120)
    ax.plot(x, y_plot, linewidth=2, label="Wrist (smoothed)")
    ax.axvspan(swing_start, swing_end, alpha=0.10, label="Swing window")

    colors = {
        "Address": "#d3d3d3",
        "Backswing": "#87cefa",
        "Top": "#ffa07a",
        "Downswing": "#98fb98",
        "Impact": "#ffd700",
        "Follow Through": "#dda0dd",
    }
    for name, (l, r) in phase_ranges.items():
        if l >= r:
            continue
        ax.axvspan(l, r, alpha=0.25, color=colors.get(name, "#cccccc"), label=name)

    handles, labels = ax.get_legend_handles_labels()
    uniq = {}
    for h, lab in zip(handles, labels):
        uniq[lab] = h
    ax.legend(uniq.values(), uniq.keys(), loc="best", fontsize=9, frameon=False)

    ax.set_xlabel("Frame")
    ax.set_ylabel("Wrist Height (flipped)")
    ax.set_title(title)
    ax.grid(True, linewidth=0.5, alpha=0.4)
    plt.tight_layout()
    plt.show()

def plot_hand_path_2d(hand_path: dict, 
                      ott_analysis: dict,
                      video_width: int,
                      video_height: int,
                      title: str = "Hand Path Analysis"):
    """
    Plot 2D hand path with OTT danger zones highlighted.
    
    Args:
        hand_path: from extract_hand_path()
        ott_analysis: from analyze_ott_deviation()
        video_width, video_height: for scaling
        title: plot title
    """
    xs = hand_path["xs"]
    ys = hand_path["ys"]
    
    # Flip Y so "up" is up
    ys_plot = video_height - ys
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=120)
    
    # === LEFT PLOT: 2D Hand Path ===
    ax1.plot(xs, ys_plot, 'o-', linewidth=2, markersize=4, 
             color='#2E86AB', label='Hand Path')
    
    # Mark start and end
    ax1.plot(xs[0], ys_plot[0], 'o', markersize=12, 
             color='green', label='Top of Backswing', zorder=10)
    ax1.plot(xs[-1], ys_plot[-1], 'o', markersize=12, 
             color='red', label='Impact Zone', zorder=10)
    
    # Add arrows to show direction
    n = len(xs)
    for i in range(0, n-1, max(1, n//10)):  # ~10 arrows
        if i+1 < n:
            dx = xs[i+1] - xs[i]
            dy = ys_plot[i+1] - ys_plot[i]
            ax1.arrow(xs[i], ys_plot[i], dx*0.8, dy*0.8,
                     head_width=15, head_length=10, 
                     fc='gray', ec='gray', alpha=0.3)
    
    # OTT danger zone (depends on golfer handedness)
    # This is simplified - assuming right-handed, face-on view
    top_x = ott_analysis["details"]["top_x_position"] * video_width
    
    # Zone where hands should NOT be (outward movement)
    danger_left = max(0, top_x - video_width * 0.15)
    ax1.axvspan(danger_left, top_x, alpha=0.15, color='red', 
                label='OTT Danger Zone')
    
    # Good zone (hands staying neutral or moving inward)
    good_right = min(video_width, top_x + video_width * 0.1)
    ax1.axvspan(top_x, good_right, alpha=0.15, color='green',
                label='Good Path Zone')
    
    ax1.set_xlabel('Horizontal Position (pixels)', fontsize=11)
    ax1.set_ylabel('Vertical Position (pixels, flipped)', fontsize=11)
    ax1.set_title(f'{title}\nOTT Score: {ott_analysis["ott_score"]:.1f}/10', 
                  fontsize=13, fontweight='bold')
    ax1.legend(loc='best', fontsize=9, framealpha=0.9)
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal', adjustable='box')
    
    # === RIGHT PLOT: Lateral Movement Over Time ===
    frames = hand_path["frame_idxs"]
    
    # Normalize X positions relative to starting position
    xs_relative = xs - xs[0]
    
    ax2.plot(frames, xs_relative, 'o-', linewidth=2, markersize=3,
             color='#A23B72')
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Highlight OTT threshold
    ax2.axhspan(-50, 0, alpha=0.2, color='red', label='OTT Movement')
    ax2.axhspan(0, 30, alpha=0.2, color='green', label='Good Movement')
    
    ax2.set_xlabel('Frame Number', fontsize=11)
    ax2.set_ylabel('Lateral Movement (pixels from top)', fontsize=11)
    ax2.set_title('Lateral Hand Movement\n(Top → Impact)', fontsize=13)
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # Add metrics text
    metrics_text = (
        f"Movement: {ott_analysis['movement_direction']}\n"
        f"Shift: {ott_analysis['lateral_movement']:.1f}px\n"
        f"Confidence: {ott_analysis['confidence']:.0%}"
    )
    ax2.text(0.02, 0.98, metrics_text,
             transform=ax2.transAxes,
             fontsize=10,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.show()

def plot_xy_phases(xs: np.ndarray, 
                   ys: np.ndarray,
                   phase_ranges: dict,
                   swing_start: int,
                   swing_end: int,
                   video_height: int,
                   title: str = "Hand Position - X and Y"):
    """
    Plot both X and Y trajectories with phase bands.
    Helps visualize lateral movement alongside vertical.
    """
    x_axis = np.arange(len(xs))
    
    # Interpolate for smooth plotting
    xs_smooth = interpolate_nans(moving_average(xs, 5))
    ys_smooth = interpolate_nans(moving_average(ys, 5))
    ys_plot = video_height - ys_smooth  # Flip Y
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), dpi=120,
                                    sharex=True)
    
    colors = {
        "Address": "#d3d3d3",
        "Backswing": "#87cefa",
        "Top": "#ffa07a",
        "Downswing": "#98fb98",
        "Impact": "#ffd700",
        "Follow Through": "#dda0dd",
    }
    
    # === PLOT 1: Vertical (Y) ===
    ax1.plot(x_axis, ys_plot, linewidth=2, color='#2E86AB', 
             label='Wrist Height')
    
    for name, (l, r) in phase_ranges.items():
        if l >= r:
            continue
        ax1.axvspan(l, r, alpha=0.25, color=colors.get(name, "#cccccc"))
    
    ax1.set_ylabel('Vertical Position (flipped)', fontsize=11)
    ax1.set_title(title, fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best', fontsize=9)
    
    # === PLOT 2: Lateral (X) - Key for OTT ===
    ax2.plot(x_axis, xs_smooth, linewidth=2, color='#A23B72',
             label='Wrist Lateral')
    
    for name, (l, r) in phase_ranges.items():
        if l >= r:
            continue
        ax2.axvspan(l, r, alpha=0.25, color=colors.get(name, "#cccccc"),
                   label=name if name not in ['Address'] else None)
    
    ax2.axvspan(swing_start, swing_end, alpha=0.10, 
                color='black', label='Swing Window')
    
    ax2.set_xlabel('Frame', fontsize=11)
    ax2.set_ylabel('Lateral Position (pixels)', fontsize=11)
    ax2.set_title('Lateral Movement (X) - Key for Over-the-Top Detection',
                  fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Deduplicate legend
    handles, labels = ax2.get_legend_handles_labels()
    unique = {}
    for h, l in zip(handles, labels):
        unique[l] = h
    ax2.legend(unique.values(), unique.keys(), 
               loc='best', fontsize=9, framealpha=0.9)
    
    plt.tight_layout()
    plt.show()