"""
MediaPipe Pose renderer for video frames.

"""


# Imports
import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Optional

mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

def draw_pose_on_frame(video_path: str, frame_idx: int,
                       model_complexity: int = 1,
                       vis_thresh: float = 0.3):
    """
    Returns (rgb_frame_with_skeleton, success_flag).
    - Seeks to frame_idx in the video
    - Runs MediaPipe Pose
    - Draws skeleton if detected
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[warn] Could not open video: {video_path}")
        return None, False

    # Seek to frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, int(frame_idx)))
    ok, frame = cap.read()
    if not ok or frame is None:
        cap.release()
        print(f"[warn] Could not read frame {frame_idx}")
        return None, False

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(model_complexity=model_complexity,
                      enable_segmentation=False) as pose:
        res = pose.process(rgb)

    if res.pose_landmarks is not None:
        # Optional: drop low-visibility landmarks (kept for drawing completeness)
        annotated = rgb.copy()
        mp_drawing.draw_landmarks(
            annotated,
            res.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_styles.get_default_pose_landmarks_style()
        )
    else:
        annotated = rgb.copy()
        # no landmarks; still return the raw frame for context

    cap.release()
    return annotated, True

def draw_pose_on_multiple_frames(
    video_path: str,
    frame_indices: list,
    model_complexity: int = 1
) -> dict:
    """Draw pose skeletons on multiple frames efficiently."""
    results = {}
    
    for idx in frame_indices:
        frame, success = draw_pose_on_frame(
            video_path, 
            idx, 
            model_complexity=model_complexity
        )
        results[idx] = (frame, success)
    
    return results