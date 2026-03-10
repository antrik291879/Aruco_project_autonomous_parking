# Aruco_project_autonomous_parking

The project is based on computer vision. We used Bluetooth for wireless communication between the PC and the microcontroller installed on the car.

The goal of the project was to park a randomly placed car in a specific parking spot. To achieve this, we studied concepts such as computer vision, pixel mapping, and image processing in order to recognize a square marked on the floor and determine each spot within the square as coordinates with respect to the corners of the square.

We also studied concepts of object detection, including contour detection, Gaussian blur, kernel size, and grayscale processing. Additionally, we explored perspective transformation and warp transformation to obtain a bird’s-eye view of the area.

During this process, we learned about ArUco markers. The computer could detect these markers and determine the pixel locations of the markers’ corners, storing them in an array in a specific order for each marker ID.

We used this capability for our purpose because we needed pixel coordinates as the source points in the warpPerspective transformation function in the OpenCV library. The destination points were defined as (0,0), (480,0), (0,480), and (480,480) since our square area was 4 ft × 4 ft.

We attached a fifth ArUco marker diagonally on the car so that in the bird’s-eye view we could subtract the bottom corner coordinates from the top corner coordinates to obtain the vector representing the direction in which the car is facing:

(𝑥1 − 𝑥2, 𝑦1 − 𝑦2)

We assigned the top corner as the coordinate of the car, as the car would rotate about an axis passing through this point.

Since we now had both the direction coordinates and the position coordinates of the car, along with the destination coordinates, we were able to guide the car to the destination using a simple algorithm.

While designing the algorithm and writing the code, we had to consider tolerance levels and motor RPM, as they needed to be optimal due to the time difference between the video feed and Bluetooth transmission.
