README
======

Project Title
-------------

Video Monitoring System with QR Code and ArUco Marker Detection

Introduction
------------

This project implements a video monitoring system that captures a video stream from an IP camera, performs QR code and ArUco marker detection, and provides real-time feedback. The system is designed to calculate the depth and size of detected ArUco markers, making it suitable for various applications, such as surveillance and object tracking.

Prerequisites
-------------

Ensure you have the following dependencies installed:

*   OpenCV (`cv2`)
*   NumPy (`numpy`)
*   `mycsv` module
*   `ptz_qrdetection` module
*   `rtsp` module
*   GObject
*   Gst (GStreamer)
*   GstRtspServer

You can install the required Python packages using:

bashCopy code

`pip install opencv-python numpy rtsp`

For other modules (`mycsv`, `ptz_qrdetection`, etc.), follow the respective installation instructions provided with those modules.

Usage
-----

1.  Clone the repository:
    
    bashCopy code
    
    `git clone <repository-url> cd <repository-directory>`
    
2.  Run the `start_video_system` function in the `main.py` file:
    
    bashCopy code
    
    `python main.py`
    
    This will initiate the video monitoring system.
    
3.  Adjust system parameters in the `start_video_system` function, such as the RTSP URL, pixel sizes, and other configuration options.
    

Configuration
-------------

*   **RTSP URL Configuration:**
    
    pythonCopy code
    
    `cap = IpVideoCapture('rtsp://<username>:<password>@<camera-ip>:<port>/0/onvif/profile2/media.smp')`
    
    Replace `<username>`, `<password>`, `<camera-ip>`, and `<port>` with your camera's login credentials and IP address.
    
*   **Pixel Size Configuration:**
    
    pythonCopy code
    
    `pixel_size_50 = 280  # TODO: Adjust as needed pixel_size_100 = 560  # TODO: Adjust as needed`
    
    Modify `pixel_size_50` and `pixel_size_100` according to your specific requirements.
    

Functionality
-------------

*   **QR Code Detection:**
    
    The system detects QR codes in the video stream using the `detector.qr_detection` method.
    
*   **ArUco Marker Detection:**
    
    ArUco markers are detected, and their depth and size are calculated using the `convert_depth` and `convert_real_size` methods.
    
*   **Real-time Display:**
    
    The processed video frames are displayed in real-time, and the ArUco markers are highlighted based on their depth.
    
*   **Server (Optional):**
    
    An optional RTSP server is implemented for streaming purposes. Enable the `is_stream` variable to activate the server.
    

Customization
-------------

Feel free to customize the code according to your specific needs. Adjustments can be made to the RTSP URL, pixel sizes, and any other parameters based on the requirements of your surveillance or monitoring application.

License
-------

This project is licensed under the [MIT License](LICENSE).

Acknowledgments
---------------

*   This project utilizes the capabilities of OpenCV, NumPy, and other related libraries.
*   Special thanks to the authors of the external modules (`mycsv`, `ptz_qrdetection`, etc.) for their contributions.

* * *

Feel free to add more sections or details based on the specific features and requirements of your project.
