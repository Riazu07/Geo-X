# Geo-X
Autonomous Mobile Manipulation Rover for Hazardous Environment Exploration and Sample Acquisition
# Geo-X

## Autonomous Mobile Manipulation Rover for Hazardous Environment Exploration and Sample Acquisition

Geo-X is an autonomous mobile manipulation rover designed for exploration, environmental monitoring, localization, navigation, and sample acquisition in hazardous and unstructured environments.

The system integrates a Raspberry Pi 5-based ROS 2 robotic architecture with LiDAR, IMU, GPS, environmental sensors, power monitoring, a mobile rover platform, and a 6-DOF robotic arm. The rover is designed to collect environmental information, navigate its surroundings, and perform sample-handling operations while reducing direct human exposure to hazardous environments.

---

## 🚀 Key Features

- 🤖 Autonomous mobile rover platform
- 🧭 LiDAR-based environment perception and navigation
- 📍 GPS-based localization
- 🌐 IMU-based orientation and motion sensing
- 🌫️ Environmental gas monitoring
- 🌡️ Temperature and humidity monitoring
- 🔋 Battery voltage and current monitoring
- 🦾 6-DOF robotic arm for sample acquisition
- 🎮 Manual arm/rover control for testing and operation
- 🖥️ ROS 2-based modular software architecture
- 🧠 Raspberry Pi 5 edge processing
- 📊 RViz2-based visualization and monitoring

---

## 🧩 System Components

| Subsystem | Component |
|---|---|
| Main Computer | Raspberry Pi 5 |
| Operating System | Ubuntu 24.04 |
| Robotics Framework | ROS 2 |
| LiDAR | YDLIDAR |
| IMU | GY-91 |
| GPS | GPS module |
| Gas Monitoring | MQ-135 |
| Temperature/Humidity | DHT11 |
| Power Monitoring | INA219 |
| Robotic Arm | 6-DOF Arm |
| Servo Controller | PCA9685 |
| Rover Drive | Differential Drive |
| Visualization | RViz2 |

---

## 🏗️ ROS 2 Packages

The workspace contains the following Geo-X packages:

- `geox_base` – Rover base and mobile platform control
- `geox_arm` – 6-DOF robotic arm control
- `geox_arm_teleop` – Manual arm control
- `geox_gps` – GPS localization
- `geox_imu` – IMU sensing and orientation
- `geox_gas` – Gas sensor monitoring
- `geox_dht11` – Temperature and humidity monitoring
- `geox_ina219` – Battery voltage/current monitoring
- `ydlidar_ros2_driver` – LiDAR integration
- `YDLidar-SDK` – LiDAR communication library

---

## 🧠 System Architecture

Geo-X follows a modular ROS 2 architecture in which individual sensors and actuators are handled by dedicated ROS 2 nodes.

Sensor data is collected by the Raspberry Pi 5 and distributed through ROS 2 topics. LiDAR and IMU data support environmental perception and robot motion awareness, while GPS provides localization information. Environmental sensors monitor hazardous conditions, and the INA219 provides electrical power measurements.

The 6-DOF robotic arm is controlled through the PCA9685 servo controller and is used for sample acquisition and manipulation tasks.

RViz2 provides visualization of the robot, LiDAR data, coordinate frames, and other ROS 2 information during development and testing.

---

## 📁 Repository Structure

```text
Geo-X/
├── src/
│   ├── geox_arm/
│   ├── geox_arm_teleop/
│   ├── geox_base/
│   ├── geox_dht11/
│   ├── geox_gas/
│   ├── geox_gps/
│   ├── geox_imu/
│   ├── geox_ina219/
│   ├── YDLidar-SDK/
│   └── ydlidar_ros2_driver/
│
├── .gitignore
└── README.md
