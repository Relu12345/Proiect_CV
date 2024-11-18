import cv2
from hand_tracking import process_frame, draw_hand_landmarks
from key_input import PressKey, ReleaseKey, KEY_W, KEY_A, KEY_S, KEY_D
from utils import calculate_distance

screen_center = 320

def main():
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        result = process_frame(frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                draw_hand_landmarks(frame, hand_landmarks)

                landmarks = hand_landmarks.landmark
                thumb_tip = landmarks[4]  # Thumb tip
                index_tip = landmarks[8]  # Index tip
                wrist = landmarks[0]     # Wrist

                thumb_index_dist = calculate_distance(thumb_tip, index_tip)

                if thumb_index_dist < 0.05:
                    PressKey(KEY_W)
                    ReleaseKey(KEY_S)
                else:
                    PressKey(KEY_S)
                    ReleaseKey(KEY_W)

                hand_center_x = wrist.x * frame.shape[1]
                if hand_center_x < screen_center - 100:
                    PressKey(KEY_A)
                    ReleaseKey(KEY_D)
                elif hand_center_x > screen_center + 100:
                    PressKey(KEY_D)
                    ReleaseKey(KEY_A)
                else:
                    ReleaseKey(KEY_A)
                    ReleaseKey(KEY_D)

        cv2.imshow("Hand Control", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
