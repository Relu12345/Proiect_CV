import cv2
import mediapipe as mp
import ctypes
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

screen_center = 320

# DirectInput Scan Codes for W, A, S, D
KEY_W = 0x11
KEY_A = 0x1E
KEY_S = 0x1F
KEY_D = 0x20

# C struct redefinitions for DirectInput
PUL = ctypes.POINTER(ctypes.c_ulong)


# Taken from https://stackoverflow.com/questions/14489013/simulate-python-keypresses-for-controlling-a-game
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Keep a key down until you can't see it anymore
def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Release that bad boy
def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def main():
    # Initialize the camera and keep taking frames
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally and convert color for MediaPipe
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Draw landmarks on frame
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get coordinates for landmarks to detect gestures and positions
                landmarks = hand_landmarks.landmark
                thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
                wrist = landmarks[mp_hands.HandLandmark.WRIST]

                # Calculate Euclidean distance between thumb and index for open/closed gesture (Help from a friend :D )
                thumb_index_dist = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5

                # If the thumb and index are close/far, go forward/back
                if thumb_index_dist < 0.05:
                    PressKey(KEY_W)
                    ReleaseKey(KEY_S)
                else:
                    PressKey(KEY_S)
                    ReleaseKey(KEY_W)

                # Same, but using the position of the hand to go left/right
                hand_center_x = wrist.x * frame.shape[1]
                if hand_center_x < screen_center - 100:
                    PressKey(KEY_A)  # Left side
                    ReleaseKey(KEY_D)
                elif hand_center_x > screen_center + 100:
                    PressKey(KEY_D)  # Right side
                    ReleaseKey(KEY_A)
                else:
                    ReleaseKey(KEY_A)
                    ReleaseKey(KEY_D)

if __name__ == "__main__":
    main()
