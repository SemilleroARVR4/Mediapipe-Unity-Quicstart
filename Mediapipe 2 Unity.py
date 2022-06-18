import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
mp_pose.SMOOTH_LANDMARKS = True
mp_pose.MODEL_COMPLEXITY = 1

import socket

UDP_IP = "localhost"
UDP_PORT = 11111
UDP_PORTWorld = 11112
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as pose:


    while cap.isOpened():
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

      # To improve performance, optionally mark the image as not writeable to
      # pass by reference.
      
      image.flags.writeable = False
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      results = pose.process(image)
      height, width, _ = image.shape
      # Draw the pose annotation on the image.
      image.flags.writeable = True
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

      if(results.pose_landmarks is not None):
        data = ""
        for landmark in results.pose_landmarks.landmark:
          data  += f"{landmark.x:.5f}" + ", " + f"{landmark.y:.5f}" + ", " + f"{landmark.z:.5f}" + ';'
        sock.sendto(data.encode(), (UDP_IP, UDP_PORT))

      if(results.pose_world_landmarks is not None):
        data = ""
        for landmark in results.pose_world_landmarks.landmark:
          data  += f"{landmark.x:.5f}" + ", " + f"{landmark.y:.5f}" + ", " + f"{landmark.z:.5f}" + ';'
        sock.sendto(data.encode(), (UDP_IP, UDP_PORTWorld))
          

      mp_drawing.draw_landmarks(
          image,
          results.pose_landmarks,
          mp_pose.POSE_CONNECTIONS,
          landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
      
      # Flip the image horizontally for a selfie-view display.
      cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
      if cv2.waitKey(5) & 0xFF == 27:
        break

sock.close
cap.release()