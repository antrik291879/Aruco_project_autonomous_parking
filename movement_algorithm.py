import math

def movement_command(robot_coordinates, target_coordinates, robot_angle, stage):
    x_robot, y_robot = robot_coordinates
    x_target, y_target = target_coordinates

    tolerance_angle = 15  
    tolerance_dist = 30    

    dx = x_target - x_robot
    dy = y_target - y_robot
    desired_angle = math.degrees(math.atan2(dy, dx))
    angle_error = ((desired_angle - robot_angle + 180) % 360) - 180
    distance = math.hypot(dx, dy)

    if stage == 1:
        if abs(angle_error) > tolerance_angle:
            if angle_error > 0:
                cmd = 'L' 
            else: 
                cmd='R'
            return stage, cmd
        else:
            stage = 2
            cmd='S'
            return stage, cmd

    elif stage == 2:
        if distance > tolerance_dist:
            cmd='F'
            return stage, cmd
        else:
            cmd="S"
            stage = 3
            return stage, cmd

    elif stage == 3:
        if abs(angle_error) > tolerance_angle:
            cmd = 'L' if angle_error > 0 else 'R'
            return stage, cmd
        else:
            cmd='S'
            stage = 4
            return stage, cmd

    else:
        cmd='S'
        return stage,cmd
