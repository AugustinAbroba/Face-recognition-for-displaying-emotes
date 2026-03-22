import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import os
import ctypes

mp_face = mp.solutions.face_mesh
mp_draw = mp.solutions.drawing_utils

face_mesh = mp_face.FaceMesh(max_num_faces=1, refine_landmarks=True)
cap = cv2.VideoCapture(0)

emotes = {}
emotes_dir = r"C:\Users\user\Downloads\pngtuber\emotes"

for emotion in ["idle","talk","blink","sad","angry","happy","surprise"]:
    path = os.path.join(emotes_dir,f"{emotion}.png")
    if os.path.exists(path):
        emotes[emotion] = cv2.imread(path,cv2.IMREAD_UNCHANGED)

emotion_buffer = deque(maxlen=8)
mode = 5

def dist(a,b):
    return np.linalg.norm(np.array(a)-np.array(b))

def overlay_png(bg, png, x, y):
    if png is None:
        return bg

    h, w = png.shape[:2]
    x = max(0, min(x, bg.shape[1]-w))
    y = max(0, min(y, bg.shape[0]-h))

    if png.shape[2] == 4:
        alpha = png[:,:,3]/255.0
        for c in range(3):
            bg[y:y+h,x:x+w,c] = alpha*png[:,:,c] + (1-alpha)*bg[y:y+h,x:x+w,c]
    else:
        bg[y:y+h,x:x+w] = png[:,:,:3]

    return bg

# 🔥 fechar janela sem crash
def close_window(name):
    try:
        cv2.destroyWindow(name)
    except:
        pass

# 🔥 transparência real
def make_window_transparent(window_name):
    hwnd = ctypes.windll.user32.FindWindowW(None, window_name)
    styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles | 0x80000)
    ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 255, 0x2)

transparent_applied = False

while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame,1)
    h,w,_ = frame.shape
    clean_frame = frame.copy()

    rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    emotion = "idle"
    face_x, face_y = w//2, h//2

    if results.multi_face_landmarks:

        face = results.multi_face_landmarks[0]
        landmarks = [(int(lm.x*w), int(lm.y*h)) for lm in face.landmark]

        nose = landmarks[1]
        face_x, face_y = nose

        mouth_top = landmarks[13]
        mouth_bottom = landmarks[14]
        mouth_left = landmarks[61]
        mouth_right = landmarks[291]

        eye_top = landmarks[159]
        eye_bottom = landmarks[145]

        brow_left_y = landmarks[70][1]
        brow_right_y = landmarks[300][1]
        eye_left_y = landmarks[159][1]
        eye_right_y = landmarks[386][1]

        brow_diff = ((eye_left_y - brow_left_y) + (eye_right_y - brow_right_y)) / 2

        face_width = dist(landmarks[234],landmarks[454])

        mouth_ratio = dist(mouth_top,mouth_bottom) / face_width
        eye_ratio = dist(eye_top,eye_bottom) / face_width
        smile_ratio = dist(mouth_left,mouth_right) / face_width
        brow_ratio = brow_diff / face_width

        if eye_ratio < 0.045:
            emotion = "blink"
        elif brow_ratio < 0.06 and smile_ratio < 0.47:
            emotion = "angry"
        elif smile_ratio > 0.45:
            emotion = "happy"
        elif mouth_ratio > 0.15:
            emotion = "surprise"
        elif mouth_ratio > 0.055:
            emotion = "talk"
        else:
            emotion = "idle"

        if mode == 4:
            mp_draw.draw_landmarks(frame, face, mp_face.FACEMESH_CONTOURS)

    emotion_buffer.append(emotion)
    emotion = max(set(emotion_buffer), key=emotion_buffer.count)

    emote = emotes.get(emotion, None)
    if emote is not None:
        emote = cv2.resize(emote, (0,0), fx=0.4, fy=0.4)

    emote_canvas = np.zeros((h,w,3), dtype=np.uint8)
    if emote is not None:
        emote_canvas = overlay_png(emote_canvas, emote, w//2-325, h//2-245)

    # ===== MODOS =====

    if mode == 1:
        cv2.imshow("EMOTE", emote_canvas)
        cv2.resizeWindow("EMOTE", 200, 200)
        if not transparent_applied:
            make_window_transparent("EMOTE")
            transparent_applied = True

    elif mode == 2:
        cv2.imshow("EMOTE", emote_canvas)
        cv2.imshow("CAMERA", clean_frame)
        cv2.resizeWindow("EMOTE", 200, 200)
    elif mode == 3:
        if emote is not None:
            side = np.zeros((h,200,3), dtype=np.uint8)
            side = overlay_png(side, emote, 0, h//2-100)
            output = np.hstack((clean_frame, side))
        else:
            output = clean_frame
        cv2.imshow("PNGtuber", output)

    elif mode == 4:
        if emote is not None:
            side = np.zeros((h,200,3), dtype=np.uint8)
            side = overlay_png(side, emote, 0, h//2-100)
            output = np.hstack((frame, side))
        else:
            output = frame
        cv2.imshow("PNGtuber", output)

    elif mode == 5:
        output = frame.copy()
        if emote is not None:
            output = overlay_png(output, emote, face_x-100, face_y-100)
        cv2.imshow("PNGtuber", output)

    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break

    elif key == ord('1'):
        mode = 1
        close_window("PNGtuber")
        close_window("CAMERA")

    elif key == ord('2'):
        mode = 2
        close_window("PNGtuber")

    elif key == ord('3'):
        mode = 3
        close_window("CAMERA")
        close_window("EMOTE")

    elif key == ord('4'):
        mode = 4
        close_window("CAMERA")
        close_window("EMOTE")

    elif key == ord('5'):
        mode = 5
        close_window("CAMERA")
        close_window("EMOTE")

cap.release()
cv2.destroyAllWindows()
