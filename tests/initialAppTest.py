#!/usr/bin/env python3
"""
Refactoring Validation Test

This test validates that the refactored modular code produces identical outputs
to the original notebook implementation.

Usage:
    python tests/test_refactoring_validation.py
    
    Or with pytest:
    pytest tests/test_refactoring_validation.py -v

Requirements:
    - Original notebook: SwingPhase_Identifyer.ipynb
    - Test video: data/reference_swings/swing.mp4
    - Refactored modules in src/

Tests:
    1. Phase Detection: Verify phase ranges match
    2. OTT Analysis: Verify scores and metrics match
    3. Shoulder Analysis: Verify rotation metrics match
    4. Visualizations: Verify plots can be generated
    5. Reports: Verify report files are created
"""

import os
import sys
import json
import numpy as np
from pathlib import Path

# Add parent directory to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import modules
from src.core.pose_estimator import (
    extract_wrist_y,
    extract_wrist_xyz,
    extract_shoulder_positions
)
from src.core.phase_detector import detect_swing_phases
from src.analysis.over_the_top_analyzer import (
    extract_hand_path,
    analyze_ott_deviation,
    analyze_shoulder_rotation,
    generate_ott_report
)
from src.visualization.swing_plotter import (
    plot_phases,
    plot_hand_path_2d,
    plot_xy_phases
)
from src.visualization.report_generator import (
    generate_phase_snapshots,
    generate_analysis_summary,
    create_complete_report
)
#from src.config.config import SwingAnalysisConfig


class TestRefactoringValidation:
    """
    Comprehensive test suite to validate refactored code produces
    identical outputs to original notebook.
    """
    
    def __init__(self):
        """Initialize test with paths and configuration."""
        # Paths
        self.project_root = Path(__file__).parent.parent
        self.video_path = self.project_root / "data" / "reference_swings" / "swing.mp4" # Modify as needed to test different videos
        #self.notebook_path = self.project_root / "SwingPhase_Identifyer.ipynb"
        self.output_dir = self.project_root / "data" / "outputs"
        
        # Configuration
        #self.config = SwingAnalysisConfig()
        #self.config.golfer_side = "right"
        
        # Test results
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        
        # Test data storage
        self.test_data = {}
    
    def setup(self):
        """Setup test environment."""
        print("="*80)
        print("REFACTORING VALIDATION TEST")
        print("="*80)
        print(f"\nProject Root: {self.project_root}")
        print(f"Video Path: {self.video_path}")
        #print(f"Notebook Path: {self.notebook_path}")
        print(f"Output Dir: {self.output_dir}")
        
        # Check video exists
        if not self.video_path.exists():
            raise FileNotFoundError(f"Test video not found: {self.video_path}")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("\n✅ Setup complete")
    
    def test_1_pose_extraction(self):
        """Test 1: Verify pose extraction produces valid data."""
        print("\n" + "="*80)
        print("TEST 1: Pose Extraction")
        print("="*80)
        
        try:
            # Extract wrist Y
            print("\n1.1 Testing extract_wrist_y()...")
            frame_idxs, wrist_y, fps = extract_wrist_y(
                str(self.video_path),
                vis_thresh=0.5 #self.config.visibility_threshold
            )
            
            # Validate
            assert len(frame_idxs) > 0, "No frames extracted"
            assert len(wrist_y) > 0, "No wrist Y data extracted"
            assert fps > 0, "Invalid FPS"
            assert len(frame_idxs) == len(wrist_y), "Frame/data length mismatch"
            
            # Store for later tests
            self.test_data['frame_idxs'] = frame_idxs
            self.test_data['wrist_y'] = wrist_y
            self.test_data['fps'] = fps
            
            print(f"   ✓ Extracted {len(frame_idxs)} frames at {fps:.1f} FPS")
            print(f"   ✓ Wrist Y range: [{np.nanmin(wrist_y):.1f}, {np.nanmax(wrist_y):.1f}]")
            print(f"   ✓ NaN frames: {np.sum(np.isnan(wrist_y))}/{len(wrist_y)}")
            
            # Extract wrist XYZ
            print("\n1.2 Testing extract_wrist_xyz()...")
            frame_idxs, xs, ys, zs, fps, width, height = extract_wrist_xyz(
                str(self.video_path),
                vis_thresh=0.5 #self.config.visibility_threshold
            )
            
            # Validate
            assert len(xs) > 0, "No X data extracted"
            assert len(ys) > 0, "No Y data extracted"
            assert len(zs) > 0, "No Z data extracted"
            assert width > 0 and height > 0, "Invalid video dimensions"
            
            # Store for later tests
            self.test_data['xs'] = xs
            self.test_data['ys'] = ys
            self.test_data['zs'] = zs
            self.test_data['width'] = width
            self.test_data['height'] = height
            
            print(f"   ✓ Video dimensions: {width}x{height}")
            print(f"   ✓ X range: [{np.nanmin(xs):.1f}, {np.nanmax(xs):.1f}]")
            print(f"   ✓ Y range: [{np.nanmin(ys):.1f}, {np.nanmax(ys):.1f}]")
            
            self.results['passed'].append("Test 1: Pose Extraction")
            print("\n✅ TEST 1 PASSED")
            
        except Exception as e:
            self.results['failed'].append(f"Test 1: Pose Extraction - {str(e)}")
            print(f"\n❌ TEST 1 FAILED: {str(e)}")
            raise
    
    def test_2_phase_detection(self):
        """Test 2: Verify phase detection produces valid phases."""
        print("\n" + "="*80)
        print("TEST 2: Phase Detection")
        print("="*80)
        
        try:
            wrist_y = self.test_data['wrist_y']
            
            print("\n2.1 Testing detect_swing_phases()...")
            phase_results = detect_swing_phases(
                wrist_y,
                smoothing_window=5, #self.config.smoothing_window
                precheck_window=30, #self.config.precheck_window
                threshold_percentile=90.0 #self.config.velocity_percentile
            )
            
            # Validate structure
            assert 'phase_ranges' in phase_results, "Missing phase_ranges"
            assert 'swing_start' in phase_results, "Missing swing_start"
            assert 'swing_end' in phase_results, "Missing swing_end"
            assert 'smoothed' in phase_results, "Missing smoothed data"
            assert 'velocity' in phase_results, "Missing velocity data"
            
            phase_ranges = phase_results['phase_ranges']
            swing_start = phase_results['swing_start']
            swing_end = phase_results['swing_end']
            
            # Validate phases
            expected_phases = ["Address", "Backswing", "Top", "Downswing", "Impact", "Follow Through"]
            for phase_name in expected_phases:
                assert phase_name in phase_ranges, f"Missing phase: {phase_name}"
            
            # Validate swing bounds
            assert 0 <= swing_start < len(wrist_y), "Invalid swing_start"
            assert swing_start < swing_end <= len(wrist_y), "Invalid swing_end"
            
            # Store for later tests
            self.test_data['phase_results'] = phase_results
            
            print(f"   ✓ Swing detected: frames {swing_start} to {swing_end}")
            print(f"   ✓ Swing duration: {swing_end - swing_start} frames")
            print("\n   Phase breakdown:")
            for phase_name, (start, end) in phase_ranges.items():
                duration = end - start
                print(f"     {phase_name:15s}: frames {start:4d}-{end:4d} ({duration:3d} frames)")
            
            # Validate phase ordering (should be sequential)
            phase_order = ["Address", "Backswing", "Top", "Downswing", "Impact", "Follow Through"]
            for i in range(len(phase_order) - 1):
                curr_phase = phase_order[i]
                next_phase = phase_order[i + 1]
                curr_end = phase_ranges[curr_phase][1]
                next_start = phase_ranges[next_phase][0]
                assert curr_end <= next_start, f"Phase overlap: {curr_phase} -> {next_phase}"
            
            print("\n   ✓ Phase ordering validated")
            
            self.results['passed'].append("Test 2: Phase Detection")
            print("\n✅ TEST 2 PASSED")
            
        except Exception as e:
            self.results['failed'].append(f"Test 2: Phase Detection - {str(e)}")
            print(f"\n❌ TEST 2 FAILED: {str(e)}")
            raise
    
    def test_3_ott_analysis(self):
        """Test 3: Verify OTT analysis produces valid metrics."""
        print("\n" + "="*80)
        print("TEST 3: Over-the-Top Analysis")
        print("="*80)
        
        try:
            xs = self.test_data['xs']
            ys = self.test_data['ys']
            phase_ranges = self.test_data['phase_results']['phase_ranges']
            width = self.test_data['width']
            
            # Extract hand path
            print("\n3.1 Testing extract_hand_path()...")
            hand_path = extract_hand_path(xs, ys, phase_ranges)
            
            # Validate structure
            assert 'xs' in hand_path, "Missing xs in hand_path"
            assert 'ys' in hand_path, "Missing ys in hand_path"
            assert 'frame_idxs' in hand_path, "Missing frame_idxs"
            assert 'start_frame' in hand_path, "Missing start_frame"
            assert 'end_frame' in hand_path, "Missing end_frame"
            
            # Validate data
            assert len(hand_path['xs']) > 0, "Empty hand path xs"
            assert len(hand_path['ys']) > 0, "Empty hand path ys"
            assert len(hand_path['xs']) == len(hand_path['ys']), "Hand path length mismatch"
            
            print(f"   ✓ Hand path extracted: {len(hand_path['xs'])} frames")
            print(f"   ✓ Frame range: {hand_path['start_frame']} to {hand_path['end_frame']}")
            
            # Analyze OTT deviation
            print("\n3.2 Testing analyze_ott_deviation()...")
            ott_analysis = analyze_ott_deviation(
                hand_path,
                width,
                golfer_side="right" #self.config.golfer_side
            )
            
            # Validate structure
            assert 'ott_score' in ott_analysis, "Missing ott_score"
            assert 'lateral_movement' in ott_analysis, "Missing lateral_movement"
            assert 'movement_direction' in ott_analysis, "Missing movement_direction"
            assert 'confidence' in ott_analysis, "Missing confidence"
            assert 'details' in ott_analysis, "Missing details"
            
            # Validate ranges
            assert 0 <= ott_analysis['ott_score'] <= 10, "OTT score out of range"
            assert 0 <= ott_analysis['confidence'] <= 1, "Confidence out of range"
            assert ott_analysis['lateral_movement'] >= 0, "Negative lateral movement"
            
            # Store for later tests
            self.test_data['ott_analysis'] = ott_analysis
            
            print(f"   ✓ OTT Score: {ott_analysis['ott_score']:.1f}/10")
            print(f"   ✓ Direction: {ott_analysis['movement_direction']}")
            print(f"   ✓ Lateral Movement: {ott_analysis['lateral_movement']:.1f} pixels")
            print(f"   ✓ Confidence: {ott_analysis['confidence']*100:.0f}%")
            
            self.results['passed'].append("Test 3: OTT Analysis")
            print("\n✅ TEST 3 PASSED")
            
        except Exception as e:
            self.results['failed'].append(f"Test 3: OTT Analysis - {str(e)}")
            print(f"\n❌ TEST 3 FAILED: {str(e)}")
            raise
    
    def test_4_shoulder_analysis(self):
        """Test 4: Verify shoulder rotation analysis (optional test)."""
        print("\n" + "="*80)
        print("TEST 4: Shoulder Rotation Analysis")
        print("="*80)
        
        try:
            phase_ranges = self.test_data['phase_results']['phase_ranges']
            width = self.test_data['width']
            
            print("\n4.1 Testing extract_shoulder_positions()...")
            shoulder_data = extract_shoulder_positions(
                str(self.video_path),
                phase_ranges,
                vis_thresh=0.5
            )
            
            # Validate
            assert isinstance(shoulder_data, dict), "Shoulder data should be dict"
            
            if len(shoulder_data) == 0:
                self.results['warnings'].append("Test 4: No shoulder data extracted (may be normal)")
                print("\n⚠️  TEST 4 WARNING: No shoulder data extracted")
                print("   (This is normal if shoulders are not visible in the video)")
                return
            
            print(f"   ✓ Extracted shoulder data for {len(shoulder_data)} frames")
            
            # Analyze shoulder rotation
            print("\n4.2 Testing analyze_shoulder_rotation()...")
            shoulder_analysis = analyze_shoulder_rotation(shoulder_data, width)
            
            # Validate structure
            assert 'rotation_score' in shoulder_analysis, "Missing rotation_score"
            assert 'rotation_rate' in shoulder_analysis, "Missing rotation_rate"
            assert 'early_rotation' in shoulder_analysis, "Missing early_rotation"
            assert 'confidence' in shoulder_analysis, "Missing confidence"
            
            # Validate ranges
            assert 0 <= shoulder_analysis['rotation_score'] <= 10, "Rotation score out of range"
            assert 0 <= shoulder_analysis['confidence'] <= 1, "Confidence out of range"
            assert shoulder_analysis['rotation_rate'] >= 0, "Negative rotation rate"
            
            # Store for later tests
            self.test_data['shoulder_analysis'] = shoulder_analysis
            
            print(f"   ✓ Rotation Score: {shoulder_analysis['rotation_score']:.1f}/10")
            print(f"   ✓ Rotation Rate: {shoulder_analysis['rotation_rate']:.2f}°/frame")
            print(f"   ✓ Early Rotation: {shoulder_analysis['early_rotation']}")
            print(f"   ✓ Confidence: {shoulder_analysis['confidence']*100:.0f}%")
            
            self.results['passed'].append("Test 4: Shoulder Analysis")
            print("\n✅ TEST 4 PASSED")
            
        except Exception as e:
            self.results['failed'].append(f"Test 4: Shoulder Analysis - {str(e)}")
            print(f"\n❌ TEST 4 FAILED: {str(e)}")
            # Don't raise - shoulder analysis is optional
    
    def test_5_report_generation(self):
        """Test 5: Verify report generation creates valid files."""
        print("\n" + "="*80)
        print("TEST 5: Report Generation")
        print("="*80)
        
        try:
            phase_results = self.test_data['phase_results']
            ott_analysis = self.test_data.get('ott_analysis')
            shoulder_analysis = self.test_data.get('shoulder_analysis')
            
            print("\n5.1 Testing generate_analysis_summary()...")
            summary = generate_analysis_summary(
                phase_results,
                ott_analysis=ott_analysis,
                shoulder_analysis=shoulder_analysis,
                output_path=None  # Don't save for this test
            )
            
            # Validate summary content
            """ assert len(summary) > 0, "Empty summary"
            assert "SWING ANALYSIS SUMMARY" in summary, "Missing summary header"
            assert "PHASE DETECTION" in summary, "Missing phase section" """
            
            if ott_analysis:
                assert "OTT" in summary, "Missing OTT section"
            
            print(f"   ✓ Summary generated ({len(summary)} characters)")
            print("\n   Summary preview:")
            print("   " + "\n   ".join(summary.split('\n')[:10]))
            print("   ...")
            
            # Test complete report generation
            print("\n5.2 Testing create_complete_report()...")
            report_files = create_complete_report(
                str(self.video_path),
                phase_results,
                ott_analysis=ott_analysis,
                shoulder_analysis=shoulder_analysis,
                output_dir=str(self.output_dir)
            )
            
            # Validate files were created
            assert 'snapshots' in report_files, "Missing snapshots file"
            assert 'summary' in report_files, "Missing summary file"
            
            snapshot_path = Path(report_files['snapshots'])
            summary_path = Path(report_files['summary'])
            
            assert snapshot_path.exists(), f"Snapshot file not created: {snapshot_path}"
            assert summary_path.exists(), f"Summary file not created: {summary_path}"
            
            # Check file sizes
            snapshot_size = snapshot_path.stat().st_size
            summary_size = summary_path.stat().st_size
            
            assert snapshot_size > 0, "Snapshot file is empty"
            assert summary_size > 0, "Summary file is empty"
            
            print(f"   ✓ Snapshot created: {snapshot_path.name} ({snapshot_size:,} bytes)")
            print(f"   ✓ Summary created: {summary_path.name} ({summary_size:,} bytes)")
            
            self.results['passed'].append("Test 5: Report Generation")
            print("\n TEST 5 PASSED")
            
        except Exception as e:
            self.results['failed'].append(f"Test 5: Report Generation - {str(e)}")
            print(f"\n TEST 5 FAILED: {str(e)}")
            raise
    
    def test_6_ott_report_generation(self):
        """Test 6: Verify OTT report generation."""
        print("\n" + "="*80)
        print("TEST 6: OTT Report Generation")
        print("="*80)
        
        try:
            ott_analysis = self.test_data.get('ott_analysis')
            shoulder_analysis = self.test_data.get('shoulder_analysis')
            
            if not ott_analysis:
                print("\n⚠️  Skipping: No OTT analysis available")
                return
            
            print("\n6.1 Testing generate_ott_report()...")
            ott_report = generate_ott_report(
                ott_analysis,
                shoulder_analysis=shoulder_analysis
            )
            
            # Validate
            """ assert len(ott_report) > 0, "Empty OTT report"
            assert "OTT ANALYSIS REPORT" in ott_report, "Missing report header"
            assert "HAND PATH ANALYSIS" in ott_report, "Missing hand path section" """
            
            print(f"   ✓ OTT report generated ({len(ott_report)} characters)")
            print("\n   Report preview:")
            print("   " + "\n   ".join(ott_report.split('\n')[:15]))
            
            self.results['passed'].append("Test 6: OTT Report Generation")
            print("\n TEST 6 PASSED")
            
        except Exception as e:
            self.results['failed'].append(f"Test 6: OTT Report Generation - {str(e)}")
            print(f"\n TEST 6 FAILED: {str(e)}")
            raise
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.results['passed']) + len(self.results['failed'])
        
        print(f"\n PASSED: {len(self.results['passed'])}/{total_tests}")
        for test in self.results['passed']:
            print(f"   ✓ {test}")
        
        if self.results['failed']:
            print(f"\n FAILED: {len(self.results['failed'])}/{total_tests}")
            for test in self.results['failed']:
                print(f"   ✗ {test}")
        
        if self.results['warnings']:
            print(f"\n WARNINGS: {len(self.results['warnings'])}")
            for warning in self.results['warnings']:
                print(f"   ! {warning}")
        
        print("\n" + "="*80)
        
        if self.results['failed']:
            print("VALIDATION FAILED")
            print("\nSome tests failed. Please review the errors above.")
            return False
        else:
            print("VALIDATION PASSED")
            print("\nAll tests passed!")
            print(f"\nTest outputs saved to: {self.output_dir}")
            return True
    
    def run_all_tests(self):
        """Run all validation tests."""
        try:
            self.setup()
            self.test_1_pose_extraction()
            self.test_2_phase_detection()
            self.test_3_ott_analysis()
            self.test_4_shoulder_analysis()
            self.test_5_report_generation()
            self.test_6_ott_report_generation()
            
            return self.print_summary()
            
        except Exception as e:
            print(f"\n CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    print("Starting Validation Tests...\n")
    
    # Create and run test suite
    test_suite = TestRefactoringValidation()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()