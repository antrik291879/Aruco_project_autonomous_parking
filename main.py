import cv2
import numpy as np
import cv2.aruco as aruco
import serial
import time
import math
from movement_algorithm import movement_command
from robot_angle import robot_angle_calculate

Topleft_ID, Topright_ID, Bottomright_ID, Bottomleft_ID = 1,2,3,4
Robot_Id = 5

ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
ARUCO_PARAMS = aruco.DetectorParameters()

try:
    bluetooth = serial.Serial('COM5',9600,timeout=1)
    time.sleep(2)
except:
    bluetooth = None

def send_command(cmd):
    if bluetooth:
        bluetooth.write(cmd.encode())

adjustment_due_to_height_of_id5= 30

def get_car_center(marker_center, angle_deg, offset):
    angle_rad = math.radians(angle_deg)
    return (marker_center[0] - offset * math.cos(angle_rad),
            marker_center[1] - offset * math.sin(angle_rad))

delay_in_command = 0.5
last_command_time = 0

cap = cv2.VideoCapture(0)
M = None
stage = 1
target_pos = None
output_size = None
parking_active = False

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = aruco.detectMarkers(gray, ARUCO_DICT, parameters=ARUCO_PARAMS)
    marker_centers = {}
    if ids is not None:
        for marker, marker_id in zip(corners, ids.flatten()):
            marker_centers[int(marker_id)] = marker.reshape((4, 2)).mean(axis=0)
        if all(idx in marker_centers for idx in [1,2,3,4]):
            tl = marker_centers[1]
            tr = marker_centers[2]
            br = marker_centers[3]
            bl = marker_centers[4]
            src_points = np.float32([tl, tr, br, bl])
            width = int(max(np.linalg.norm(tr-tl), np.linalg.norm(br-bl)))
            height = int(max(np.linalg.norm(bl-tl), np.linalg.norm(br-tr)))
            output_size = (width, height)
            dst_points = np.float32([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]])
            M = cv2.getPerspectiveTransform(src_points, dst_points)
            target_pos = tuple(((tl + tr) / 2).astype(int))

    if M and output_size :
        warped = cv2.warpPerspective(frame, M, output_size)
        gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        corners_w, ids_w, _ = aruco.detectMarkers(gray_warped, ARUCO_DICT, parameters=ARUCO_PARAMS)
        display = warped.copy()
        robot_detected = False
        if ids_w is not None:
            aruco.drawDetectedMarkers(display, corners_w, ids_w)
            for marker, marker_id in zip(corners_w, ids_w.flatten()):
                corner = marker.reshape((4, 2))
                marker_center = corner.mean(axis=0)
                center_int = marker_center.astype(int)
                cv2.circle(display, tuple(center_int), 5, (0, 255, 0), -1)
                cv2.putText(display, f"ID:{marker_id}", (center_int[0]+10, center_int[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
                if marker_id == Robot_Id:
                    robot_detected = True
                    robot_angle = robot_angle_calculate(corner)
                    car_center = get_car_center(marker_center, robot_angle, adjustment_due_to_height_of_id5)
                    now = time.time()
                    if parking_active and now - last_command_time > delay_in_command:
                        stage, cmd = movement_command(car_center, target_pos, robot_angle, stage)
                        send_command(cmd)
                        last_command_time = now
        if target_pos is not None:
            cv2.circle(display, target_pos, 10, (0,0,255), 2)
            cv2.putText(display, "TARGET", (target_pos[0]+15, target_pos[1]), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
        cv2.imshow("Parking System", display)
    else:
        cv2.imshow("Calibration", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s'):
        parking_active = not parking_active
        stage = 1

cap.release()
cv2.destroyAllWindows()
if bluetooth:
    bluetooth.close()
