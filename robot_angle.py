#orientation of our aruco on vehicle will be diagonal top-left=front and bottom-right=back
import math
def robot_angle_calculate(corners):
    c1=corners[1]
    c2=corners[3]
    dif_x=c2[0]-c1[0]
    dif_y=c2[1]-c1[1]
    angle_rad=math.atan2(dif_y,dif_x)
    angle_deg=math.degrees(angle_rad)
    return angle_deg
