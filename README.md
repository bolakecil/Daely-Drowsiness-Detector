# Daely Drowsiness Detector

Welcome to the **Daely Drowsiness Detector**, an AI-IoT Project! 🚗💡 This innovative project aims to enhance driver safety by detecting drowsiness in real-time using AI and IoT technologies. Below you will find an overview of the project, descriptions of its main components, and instructions on how to get started.

## Table of Contents

- [Project Overview](#project-overview)
  - [Background](#background)
- [Main Components](#main-components)
  - [Dashboard-Website](#dashboard-website-🌐)
  - [Drowsiness-Detector](#drowsiness-detector-🧠)
  - [Drowsiness-IoT](#drowsiness-iot-⚙️)
- [Dataset](#dataset-📊)
- [Team](#team-💻✨)
- [Installation](#installation-⚙️)
- [Usage](#usage-🚀)
- [Electrical Wiring Diagram](#electrical-wiring-diagram-🔌)
- [Contributing](#contributing-🤝)
- [License](#license-📄)

## Project Overview

The **Daely Drowsiness Detector** is designed to monitor and analyze driver drowsiness in real-time. The project consists of three main parts: a Dashboard-Website, a Drowsiness-Detector system using deep learning models, and an IoT component using an ESP32-CAM to capture and send data.

### Background

#### Problem 🧩

1. **High incidence of drowsy driving**, leading to traffic accidents. 
2. **Difficulty in maintaining focus** during long or monotonous drives. 
3. **Lack of early recognition** of drowsiness signs by drivers. 
4. **Overconfidence** in drivers' ability to resist drowsiness. 
5. **Struggle to determine** the best times to rest. 

#### Solution 💡

1. **Real-Time Monitoring**: Daely uses deep learning to continuously monitor and analyze driver drowsiness. 
2. **Alert Mechanism**: Daely provides a multi-stage alert system to ensure drivers are promptly alerted based on drowsiness severity. 
3. **Web Dashboard**: Daely features a web dashboard that tracks and reports driver fatigue patterns. 

## Main Components

### Dashboard-Website 🌐

The Dashboard-Website provides a user-friendly interface where users can monitor their drowsiness occurrences, view analytics, and understand their tiredness patterns.

- **Technology**: Streamlit with Firebase integration for real-time data.
- **Features**:
  - View drowsiness occurrences 📅
  - Access analytics and patterns 📈
- **Deployment**: The dashboard is deployed at [Drowsiness Detector Dashboard](https://drowsiness-detector-dashboard.streamlit.app/).
- **Repository**: The deployed files are available in a separate repository due to storage limitations: [Drowsiness Detector Website](https://github.com/bolakecil/Drowsiness-Detector-Website).

### Drowsiness-Detector 🧠

The Drowsiness-Detector component contains the deep learning models that power the drowsiness detection system.

- **Models**:
  - YOLOv8: Trained for 20 epochs 
  - Visual Transformer (ViT): Trained for 3 epochs 
  - Stacking of YOLOv8 and ViT: Trained for 6 epochs 
- **Features**:
  - API code and modules for pushing data to the database 📡
  - Evaluation notebook with metrics: F1 Score, Precision, Recall, Accuracy, Confusion Matrix, ROC 📊

### Drowsiness-IoT ⚙️

The Drowsiness-IoT component includes the code for the ESP32-CAM, which captures images and sends data for drowsiness detection. Below is a brief overview of its functionality:

- **Components**:
  - ESP32-CAM 📷
  - LCD Display for real-time feedback 📟
  - Buzzer for alerting the driver 🔊
- **Functionality**:
  - Connects to Wi-Fi 🌐
  - Captures images and sends them to the server for analysis 🖼️
  - Displays drowsiness alerts on the LCD and sounds the buzzer 🚨
 
## Dataset 📊

The model used in this project is trained with the [Drowsiness Detection Dataset](https://universe.roboflow.com/esd-krexe/drowsiness-detection-0mcjg/dataset/1) from Roboflow. This dataset contains a wide variety of images and annotations, enabling the model to learn and recognize different signs of drowsiness effectively.

## Team 💻✨

Meet the amazing team behind this project:

| **Name**                    | **Role**                | 
|-----------------------------|-------------------------| 
| **Axel Nino Nakata**        | IoT Developer           | 
| **Jehoiada Wong**           | ML Developer            | 
| **Aretha Natalova Wahyudi** | Front End Developer     | 
| **Jessica Lynn Wibowo**     | Front End Developer     |

## Installation ⚙️

### Prerequisites

- Python 3.6 or higher 
- Jupyter Notebook 
- Arduino IDE for flashing the ESP32-CAM 🛠

### Clone the Repository

```bash
git clone https://github.com/yourusername/Daely-Drowsiness-Detector.git
cd Daely-Drowsiness-Detector
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage 🚀

### Running the Dashboard

The dashboard is already deployed and can be accessed at [Drowsiness Detector Dashboard](https://drowsiness-detector-dashboard.streamlit.app/).

### Running the Drowsiness Detector

1. Navigate to the `drowsiness-detector` directory:

   ```bash
   cd drowsiness-detector
   ```

2. Open the evaluation notebook and run the cells:

   ```bash
   jupyter notebook evaluation.ipynb
   ```

### Setting up the Drowsiness IoT ⚙️

1. Open the Arduino IDE and load the provided `.ino` file. 
2. Connect your ESP32-CAM to your computer. 
3. Configure the Wi-Fi credentials and server URL in the code. 
4. Upload the code to the ESP32-CAM. 
5. Monitor the serial output for connection and detection logs. 

## Electrical Wiring Diagram 🔌

To replicate the hardware setup for this project, please refer to the electrical wiring diagram below:

![Daely Electrical Wiring Diagram](Foto%20Electrical%20Wiring%20Diagram.png)

## Contributing 🤝

We welcome contributions! Please follow these steps to contribute:

1. Fork the repository. 
2. Create a new branch (`git checkout -b feature/your-feature-name`). 
3. Make your changes. 
4. Commit your changes (`git commit -m 'Add new feature'`). 
5. Push to the branch (`git push origin feature/your-feature-name`). 
6. Open a pull request. 

---

Thank you for your interest in the **Daely Drowsiness Detector AI-IoT Project**! If you have any questions or feedback, please feel free to reach out. Happy coding! 😊
