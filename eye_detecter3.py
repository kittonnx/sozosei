import os, sys
import cv2
import dlib
from imutils import face_utils
from scipy.spatial import distance
import time

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
face_parts_detector = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# 閉じているかどうかを判断するしきい値とタイマー変数
EYE_AR_THRESH = 0.235
CHECK_TIME = 20
CLOSE_EYES_TIME_LIMIT = 10
open_time = 0
close_time = 0
before_time = None
before_eyes_open_state = True

def calc_ear(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    eye_ear = (A + B) / (2.0 * C)
    return round(eye_ear, 3)

def eye_marker(face_mat, position):
    for i, ((x, y)) in enumerate(position):
        cv2.circle(face_mat, (x, y), 1, (255, 255, 255), -1)
        cv2.putText(face_mat, str(i), (x + 2, y - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

while True:
    tick = cv2.getTickCount()

    ret, rgb = cap.read()
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.11, minNeighbors=3, minSize=(100, 100))
    
    now_time = time.time()

    if len(faces) == 1 and before_time != None:
        x, y, w, h = faces[0, :]
        cv2.rectangle(rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)

        face_gray = gray[y :(y + h), x :(x + w)]
        scale = 480 / h
        face_gray_resized = cv2.resize(face_gray, dsize=None, fx=scale, fy=scale)

        face = dlib.rectangle(0, 0, face_gray_resized.shape[1], face_gray_resized.shape[0])
        face_parts = face_parts_detector(face_gray_resized, face)
        face_parts = face_utils.shape_to_np(face_parts)

        left_eye = face_parts[42:48]
        eye_marker(face_gray_resized, left_eye)

        left_eye_ear = calc_ear(left_eye)
        cv2.putText(rgb, "LEFT eye EAR:{} ".format(left_eye_ear), 
            (10, 100), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1, cv2.LINE_AA)

        right_eye = face_parts[36:42]
        eye_marker(face_gray_resized, right_eye)

        right_eye_ear = calc_ear(right_eye)
        cv2.putText(rgb, "RIGHT eye EAR:{} ".format(round(right_eye_ear, 3)), 
            (10, 120), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1, cv2.LINE_AA)
        
        # 1f前の情報から目を閉じているor閉じていない時間に加算
        if before_eyes_open_state:
            open_time += now_time - before_time
        else:
            close_time += now_time - before_time

        # 両方の目のEARをチェック
        if (left_eye_ear + right_eye_ear) / 2 < EYE_AR_THRESH:
            before_eyes_open_state = False            
        else:
            before_eyes_open_state = True
            
        cv2.imshow('frame_resize', face_gray_resized)
    else:
        before_eyes_open_state = False
        
    before_time = now_time
    
    # 10秒以上目を閉じていたら警告
    if close_time >= CLOSE_EYES_TIME_LIMIT:
        cv2.putText(rgb, "Sleepy eyes. Wake up!", (10, 180), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3, 1)
    
    # 20秒以上過ぎたらリセットをする
    if open_time + close_time >= CHECK_TIME:
        open_time = 0
        close_time = 0
        
    cv2.putText(rgb, "close_time:{} ".format(round(close_time,3)), 
        (10, 140), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(rgb, "open_time:{} ".format(round(open_time,3)), 
        (10, 160), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1, cv2.LINE_AA)
    cv2.putText(rgb, "total_time:{} ".format(round(open_time+close_time,3)), 
        (10, 180), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1, cv2.LINE_AA)
            

    fps = cv2.getTickFrequency() / (cv2.getTickCount() - tick)
    cv2.putText(rgb, "FPS:{} ".format(int(fps)), 
        (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow('frame', rgb)
    if cv2.waitKey(1) == 27:
        break  # esc to quit

cap.release()
cv2.destroyAllWindows()
