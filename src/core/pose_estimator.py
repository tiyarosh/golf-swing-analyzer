"""
Pose Estimation Module

This module provides functions for extracting pose-related data from golf swing videos using MediaPipe Pose. 
It focuses on key landmarks such as wrists and shoulders, enabling analysis of swing phases and movement patterns.
Functions:
    extract_wrist_y(video_path: str, vis_thresh: float = 0.4):
        Extracts the average Y-coordinate (vertical position in pixels) of the left and right wrists for each frame in a video.
        Returns frame indices, wrist-Y values (NaN when missing), and video FPS.
    extract_wrist_xyz(video_path: str, vis_thresh: float = 0.4):
        Extracts the average X, Y, and Z coordinates (pixels and relative depth) of the left and right wrists for each frame.
        Returns frame indices, X/Y/Z arrays (NaN when missing), FPS, video width, and height.
    extract_shoulder_positions(video_path: str, phase_ranges: dict, vis_thresh: float = 0.5):
        Extracts shoulder positions (X, Y, Z) for left and right shoulders during specified swing phases.
        Returns a dictionary mapping frame indices to shoulder position tuples for frames in the critical phase range.
"""

# Imports
import numpy as np
import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
from typing import Tuple, Dict

def extract_wrist_y(video_path: str, vis_thresh: float = 0.4):
    """Return frame indices, wrist-Y (pixels; NaN when missing), and FPS."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(model_complexity=1, enable_segmentation=False)

    frame_idxs = []
    ys = []

    try:
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)

            y_vals = []
            if res.pose_landmarks is not None:
                lms = res.pose_landmarks.landmark
                LW = mp_pose.PoseLandmark.LEFT_WRIST.value
                RW = mp_pose.PoseLandmark.RIGHT_WRIST.value
                for w in (LW, RW):
                    lm = lms[w]
                    if lm.visibility is None or lm.y is None:
                        continue
                    if lm.visibility >= vis_thresh:
                        y_vals.append(lm.y * height)  # pixel units

            ys.append(np.mean(y_vals) if len(y_vals) else np.nan)
            frame_idxs.append(i)
            i += 1
    finally:
        cap.release()
        pose.close()

    return frame_idxs, np.array(ys, dtype=float), fps

def extract_wrist_xyz(video_path: str, vis_thresh: float = 0.4):
    """
    Extract wrist X, Y, Z coordinates (averaged L+R wrists).
    
    Returns:
        frame_idxs: list of frame indices
        xs: numpy array of X positions (pixels, NaN when missing)
        ys: numpy array of Y positions (pixels, NaN when missing)
        zs: numpy array of Z positions (depth, relative scale)
        fps: video frame rate
        width: video width
        height: video height
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(model_complexity=1, enable_segmentation=False)

    frame_idxs = []
    xs, ys, zs = [], [], []

    try:
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)

            x_vals, y_vals, z_vals = [], [], []
            
            if res.pose_landmarks is not None:
                lms = res.pose_landmarks.landmark
                LW = mp_pose.PoseLandmark.LEFT_WRIST.value
                RW = mp_pose.PoseLandmark.RIGHT_WRIST.value
                
                for w in (LW, RW):
                    lm = lms[w]
                    if lm.visibility is None:
                        continue
                    if lm.visibility >= vis_thresh:
                        x_vals.append(lm.x * width)   # pixel X
                        y_vals.append(lm.y * height)  # pixel Y
                        z_vals.append(lm.z)           # relative depth

            xs.append(np.mean(x_vals) if len(x_vals) else np.nan)
            ys.append(np.mean(y_vals) if len(y_vals) else np.nan)
            zs.append(np.mean(z_vals) if len(z_vals) else np.nan)
            frame_idxs.append(i)
            i += 1
            
    finally:
        cap.release()
        pose.close()

    return (frame_idxs, 
            np.array(xs, dtype=float), 
            np.array(ys, dtype=float),
            np.array(zs, dtype=float),
            fps, width, height)

def extract_shoulder_positions(video_path: str, 
                               phase_ranges: dict,
                               vis_thresh: float = 0.5):
    """
    Extract shoulder positions during key swing phases.
    Shoulder early rotation is another OTT indicator.
    
    Returns:
        dict with frame_idx -> (left_shoulder_xyz, right_shoulder_xyz)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(model_complexity=1, enable_segmentation=False)
    
    # Focus on downswing phase
    start = phase_ranges.get("Top", (0, 0))[0]
    end = phase_ranges.get("Impact", (0, 0))[1]
    
    shoulder_data = {}

    try:
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            
            # Only process frames in critical range
            if start <= i <= end:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = pose.process(rgb)
                
                if res.pose_landmarks is not None:
                    lms = res.pose_landmarks.landmark
                    LS = mp_pose.PoseLandmark.LEFT_SHOULDER.value
                    RS = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
                    
                    ls = lms[LS]
                    rs = lms[RS]
                    
                    if (ls.visibility >= vis_thresh and 
                        rs.visibility >= vis_thresh):
                        shoulder_data[i] = {
                            'left': (ls.x * width, ls.y * height, ls.z),
                            'right': (rs.x * width, rs.y * height, rs.z)
                        }
            
            i += 1
            
    finally:
        cap.release()
        pose.close()
    
    return shoulder_data