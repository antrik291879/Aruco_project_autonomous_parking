import cv2
import numpy as np
import cv2.aruco as aruco
import serial
import time
import math
from movement_algorithm import movement_command
from robot_angle import robot_angle_calculate
from config import *

try:
    bluetooth = serial.Serial('COM5',9600,timeout=1)
    time.sleep(2)
    print("bluetooth connected")
except:
    bluetooth = None
    print("bluetooth not connected")

ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
ARUCO_PARAMS = aruco.DetectorParameters()

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
        for i in range(len(ids)):
            marker_id = int(ids[i])
            corner_points = corners[i].reshape((4, 2))

            center_x = (corner_points[0][0] + corner_points[1][0] + corner_points[2][0] + corner_points[3][0]) / 4
            center_y = (corner_points[0][1] + corner_points[1][1] + corner_points[2][1] + corner_points[3][1]) / 4

            marker_centers[marker_id] = (center_x, center_y)
        if all(idx in marker_centers for idx in [1,2,3,4]):
            top_left = marker_centers[1]
            top_right = marker_centers[2]
            bottom_right = marker_centers[3]
            bottom_left = marker_centers[4]
            src_points = np.float32([top_left, top_right, bottom_right, bottom_left])
            top_edge_width    = math.hypot(top_right[0] - top_left[0],    top_right[1] - top_left[1])
            bottom_edge_width = math.hypot(bottom_right[0] - bottom_left[0], bottom_right[1] - bottom_left[1])
            width = int(max(top_edge_width, bottom_edge_width))

            left_edge_height  = math.hypot(bottom_left[0] - top_left[0],   bottom_left[1] - top_left[1])
            right_edge_height = math.hypot(bottom_right[0] - top_right[0], bottom_right[1] - top_right[1])
            height = int(max(left_edge_height, right_edge_height))
            output_size = (width, height)
            dst_points = np.float32([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]])
            M = cv2.getPerspectiveTransform(src_points, dst_points)
            target_x = int((top_left[0] + top_right[0]) / 2)
            target_y = int((top_left[1] + top_right[1]) / 2)
            target_pos = (target_x, target_y)   

    if M and output_size :
        warped = cv2.warpPerspective(frame, M, output_size)
        gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        corners_w, ids_w, _ = aruco.detectMarkers(gray_warped, ARUCO_DICT, parameters=ARUCO_PARAMS)
        display = warped.copy()
        robot_detected = False
        if ids_w is not None:
            aruco.drawDetectedMarkers(display, corners_w, ids_w)
            for i in range(len(ids_w)):
                marker_id     = int(ids_w[i])
                marker_corner = corners_w[i].reshape((4, 2))

                center_x = int((marker_corner[0][0] + marker_corner[1][0] + marker_corner[2][0] + marker_corner[3][0]) / 4)
                center_y = int((marker_corner[0][1] + marker_corner[1][1] + marker_corner[2][1] + marker_corner[3][1]) / 4)
                center_int = (center_x, center_y)
                cv2.circle(display, center_int, 5, (0, 255, 0), -1)
                cv2.putText(display, f"ID:{marker_id}", (center_int[0]+10, center_int[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
                if marker_id == ROBOT_ID:
                    robot_detected = True
                    robot_angle = robot_angle_calculate(marker_corner)
                    angle_rad = math.radians(robot_angle)
                    car_x = center_x - ROBOT_MARKER_OFFSET * math.cos(angle_rad)
                    car_y = center_y - ROBOT_MARKER_OFFSET * math.sin(angle_rad)
                    car_center = (car_x,car_y)
                    now = time.time()
                    if parking_active and now - last_command_time > delay_in_command:
                        stage, cmd = movement_command(car_center, target_pos, robot_angle, stage)
                        if bluetooth:
                            bluetooth.write(cmd.encode())
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
