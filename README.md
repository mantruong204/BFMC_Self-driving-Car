# Self-driving BRAIN solution for 1/10 scale Arckerman CAR model
# Functionalities:
- Lane keeping
- Trafic light
- Trafic signs compliance
- Intersection
- Zebra Crossing & Pedestrian
- Parking
- Vehicle overtake
- Roundabout
- ...
## Utilizing:
- Using Python as main programming language, associated with OpenCV to develop Lane Follow module based on segmentation, Canny Edge, …
- Deploying YOLOv5 to detect custom objects (traffic signs and lights) and integrating YOLOv5 with Python Paralell Computing
- Performing Ultrasonics sensor data acquisition for the Pedestrians Detection module
- Working with ROS/ROS2 multiple machines: create and program packages on separated embedded computers (Jetson Nano) that share Nodes with different modules via local network.
- Jetson Nano sends setpoints to STM32-NUCLEO microcontroller to control an encoder-integrated DC Motor (Moving) and Servo Motor (steering) using PID.
## Software Diagram
![ảnh](https://github.com/mantruong204/BFMC_Self-driving-Car/assets/155959855/ea897e68-d340-41cb-80e3-baa980fc3327)
## Hardware
![ảnh](https://github.com/mantruong204/BFMC_Self-driving-Car/assets/155959855/e46581fb-8052-41fa-90ae-ca80f1f65ff2)
![vlcsnap-2024-05-23-09h51m59s362](https://github.com/mantruong204/BFMC_Self-driving-Car/assets/155959855/49a0ee04-5dbf-4ab9-8f18-fc6bad8bccb9)
![vlcsnap-2024-05-23-09h52m04s752](https://github.com/mantruong204/BFMC_Self-driving-Car/assets/155959855/0d19e35f-fa3a-4e89-af57-0741c9973bb3)


https://github.com/mantruong204/BFMC_Self-driving-Car/assets/155959855/e641cb4a-968e-467f-a9ae-c105d6d2135a

