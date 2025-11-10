
# Imports
import os
import math
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from .pose_renderer import draw_pose_on_frame

def generate_phase_snapshots(
    video_path: str,
    phase_ranges: Dict[str, Tuple[int, int]],
    output_path: Optional[str] = None,
    desired_order: Optional[List[str]] = None,
    grid_cols: int = 3,
    figsize: Tuple[int, int] = (15, 8),
    dpi: int = 130
) -> str:
    """
    Generate a grid of representative frames for each swing phase.
    
    Creates a visual report showing the midpoint frame of each phase
    with pose skeleton overlay.
    
    Args:
        video_path: Path to video file
        phase_ranges: Dict mapping phase names to (start_frame, end_frame) tuples
        output_path: Path to save output image (optional, if None will just show)
        desired_order: List of phase names in desired display order
        grid_cols: Number of columns in grid
        figsize: Figure size in inches (width, height)
        dpi: Figure DPI
        
    Returns:
        Path to saved image file (or None if not saved)
    """
    # Default phase order if not specified
    if desired_order is None:
        desired_order = [
            "Address",
            "Backswing",
            "Top",
            "Downswing",
            "Impact",
            "Follow Through",
        ]
    
    # Filter to existing phases in desired order
    phase_items = [
        (name, phase_ranges[name]) 
        for name in desired_order 
        if name in phase_ranges
    ]
    
    # Compute representative frame (midpoint) for each phase
    phase_frames = []
    for name, (l, r) in phase_items:
        # Guard against degenerate ranges
        if r <= l:
            mid = l
        else:
            mid = (l + r) // 2
        phase_frames.append((name, int(mid)))
    
    # Draw and collect images
    images = []
    for name, idx in phase_frames:
        img, ok = draw_pose_on_frame(video_path, idx)
        if not ok or img is None:
            # Create a placeholder if something goes wrong
            img = np.zeros((360, 640, 3), dtype=np.uint8)
            # Note: img is already RGB from draw_pose_on_frame when it fails
            # Add text to indicate missing frame
            import cv2
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.putText(img, "No frame / pose", (20, 180),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        images.append((name, img))
    
    # Calculate grid dimensions
    rows = math.ceil(len(images) / grid_cols)
    
    # Create figure
    fig, axes = plt.subplots(rows, grid_cols, figsize=figsize, dpi=dpi)
    axes = np.array(axes).reshape(rows, grid_cols)
    
    # Plot each phase snapshot
    for i, ax in enumerate(axes.ravel()):
        ax.axis("off")
        if i < len(images):
            name, img = images[i]
            ax.imshow(img)
            ax.set_title(f"{name}", fontsize=12, pad=8, fontweight='bold')
    
    plt.tight_layout()
    
    # Save if output path provided
    if output_path:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, bbox_inches='tight')
        print(f"Phase snapshots saved to: {output_path}")
        plt.close(fig)
        return output_path
    else:
        plt.show()
        return None

def generate_analysis_summary(
    phase_results: Dict,
    ott_analysis: Optional[Dict] = None,
    shoulder_analysis: Optional[Dict] = None,
    output_path: Optional[str] = None
) -> str:
    """Generate a text summary of the swing analysis."""
    lines = []
    """ lines.append("="*60)
    lines.append("OVER-THE-TOP (OTT) ANALYSIS REPORT")
    lines.append("="*60) """
    
    """ # Phase detection summary
    lines.append("\n PHASE DETECTION:")
    lines.append(f"  Swing Start: Frame {phase_results['swing_start']}")
    lines.append(f"  Swing End: Frame {phase_results['swing_end']}")
    
    # Phase breakdown
    lines.append("\n PHASE BREAKDOWN:")
    for phase_name, (start, end) in phase_results['phase_ranges'].items():
        duration = end - start
        lines.append(f"  {phase_name:15s}: Frames {start:4d}-{end:4d} ({duration:3d} frames)") """
    
    # OTT analysis if available
    if ott_analysis:
        # Generate and include full OTT report
        from ..analysis.over_the_top_analyzer import generate_ott_report
        ott_report = generate_ott_report(ott_analysis, shoulder_analysis)
        lines.append(ott_report)
    
    summary = "\n".join(lines)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(summary)
    
    return summary

def create_complete_report(
    video_path: str,
    phase_results: Dict,
    ott_analysis: Optional[Dict] = None,
    shoulder_analysis: Optional[Dict] = None,
    output_dir: str = "outputs"
) -> Dict[str, str]:
    """
    Create a complete analysis report with all visualizations and summaries.
    
    This is a convenience function that generates all report outputs in one call:
    - Phase snapshot grid image
    - Text analysis summary
    
    Args:
        video_path: Path to video file
        phase_results: Results from detect_swing_phases()
        ott_analysis: Optional results from analyze_ott_deviation()
        shoulder_analysis: Optional results from analyze_shoulder_rotation()
        output_dir: Directory to save output files
        
    Returns:
        Dict mapping report types to file paths:
        {
            'snapshots': 'path/to/snapshots.png',
            'summary': 'path/to/summary.txt'
        }
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract video name for file naming
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    report_files = {}
    
    # 1. Generate phase snapshots
    print("Generating phase snapshots...")
    snapshot_path = os.path.join(output_dir, f"{video_name}_phase_snapshots.png")
    generate_phase_snapshots(
        video_path,
        phase_results['phase_ranges'],
        output_path=snapshot_path
    )
    report_files['snapshots'] = snapshot_path
    
    # 2. Generate text summary
    print("Generating analysis summary...")
    summary_path = os.path.join(output_dir, f"{video_name}_analysis_summary.txt")
    generate_analysis_summary(
        phase_results,
        ott_analysis=ott_analysis,
        shoulder_analysis=shoulder_analysis,
        output_path=summary_path
    )
    report_files['summary'] = summary_path
    
    print(f"\n Complete report generated in: {output_dir}")
    print(f"   - Phase snapshots: {os.path.basename(snapshot_path)}")
    print(f"   - Analysis summary: {os.path.basename(summary_path)}")
    
    return report_files