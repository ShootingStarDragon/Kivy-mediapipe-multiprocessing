import mediapipe as mp # Import mediapipe
import cv2 # Import opencv
from icecream import ic
mp_drawing = mp.solutions.drawing_utils 
mp_holistic = mp.solutions.holistic 
import time
import os
import numpy as np
times = []

# remove all files from frames folder
def remove_files():
    for file in os.listdir("frames"):
        os.remove(os.path.join("frames", file))

remove_files()

cap = cv2.VideoCapture(0)
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    # number_of_files = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False        
        
        # time_1 = time.time()
        results = holistic.process(image)
        # time_2 = time.time()
        # times.append(time_2-time_1)
        # print("timedelta wtf why is this so fast!", time_2 - time_1, 1/60,  flush= True)
        image.flags.writeable = True   
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                 mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                                 mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                                 )
        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                 mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
                                 mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                                 )
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                                 mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                 mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                 )
        
        # print(image)
        # cv2.imshow('Raw Webcam Feed', image)

        # print(type(image))
        # write image to file on frames folder
        next_frame_number = len(os.listdir('frames'))+1
        ic(next_frame_number)
        np.save(f"frames/frame_{next_frame_number}.raw", image)

        # print("fps", 1/(sum(times)/len(times)), flush=True)

        number_of_files = len(os.listdir("frames"))
        if number_of_files > 60:
            remove_files()
        print("number of files", number_of_files, flush=True) 

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()