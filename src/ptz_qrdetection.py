import sys,os,glob
sys.path.append(os.getcwd())
import numpy as np
from datetime import datetime
import cv2
import time
import util
import queue,threading
class IpVideoCapture:

    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.name = name
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            # frame = frame[520:1079 ,480:1440 ]
            if not ret:
                self.cap = cv2.VideoCapture(self.name)
                time.sleep(1)
                continue
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)
            time.sleep(0.001)
    def release(self):
        self.cap.release()
    def read(self):
        return True, cv2.resize(self.q.get(),(1920,1080))
class ArucoMarker:
    def __init__(self, id, corners):
          self.id = id
          # Since the order of the corners is [top_right, top_left, bottom_left, bottom_right]
          self.top_right = corners[0]
          self.top_left = corners[1]
          self.bottom_left = corners[2]
          self.bottom_right = corners[3]

          # compute and store the center at initialization
          corners = np.array([self.top_right, self.top_left, self.bottom_left, self.bottom_right])
          self.center = corners.mean(axis=0).tolist()

    def __str__(self):
          return f'ID: {self.id}\nTop Right: {self.top_right}\nTop Left: {self.top_left}\nBottom Left: {self.bottom_left}\nBottom Right: {self.bottom_right}'


    # Comparison function for close match
    def is_close(self, other, tolerance=5):
          return (np.allclose(self.top_right, other.top_right, atol=tolerance) and
              np.allclose(self.top_left, other.top_left, atol=tolerance) and
              np.allclose(self.bottom_left, other.bottom_left, atol=tolerance) and
              np.allclose(self.bottom_right, other.bottom_right, atol=tolerance))

    def calculate_average_length(self):
        # Calculate the length of each side
        side1 = np.linalg.norm(np.array(self.top_right) - np.array(self.top_left))
        side2 = np.linalg.norm(np.array(self.top_left) - np.array(self.bottom_left))
        side3 = np.linalg.norm(np.array(self.bottom_left) - np.array(self.bottom_right))
        side4 = np.linalg.norm(np.array(self.bottom_right) - np.array(self.top_right))

        # Calculate and return the average length
        return (side1 + side2 + side3 + side4) / 4
    def draw_side_line(self,img,color):
        h,w,c = img.shape
        return cv2.rectangle(img,(0,0),(w,h),color,10)

    def draw_corner(self,img):
        (topLeft, topRight, bottomRight, bottomLeft) = (self.top_left,self.top_right,self.bottom_right,self.bottom_left)
        # convert each of the (x, y)-coordinate pairs to integers

        topRight = (int(topRight[0]), int(topRight[1]))
        bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
        bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
        topLeft = (int(topLeft[0]), int(topLeft[1]))

        cv2.line(img, topLeft, topRight, (0, 255, 0), 2)
        cv2.line(img, topRight, bottomRight, (0, 255, 0), 2)
        cv2.line(img, bottomRight, bottomLeft, (0, 255, 0), 2)
        cv2.line(img, bottomLeft, topLeft, (0, 255, 0), 2)
        return img

    def average_with(self, marker):
        self.top_right = np.mean([self.top_right, marker.top_right], axis=0).tolist()
        self.top_left = np.mean([self.top_left, marker.top_left], axis=0).tolist()
        self.bottom_left = np.mean([self.bottom_left, marker.bottom_left], axis=0).tolist()
        self.bottom_right = np.mean([self.bottom_right, marker.bottom_right], axis=0).tolist()
        self.center = np.mean([self.center, marker.center], axis=0).tolist()
def unique_markers(markers, tolerance=20):
    # Assume that the ArucoMarker object has an average method to consolidate two markers.
    # This method should modify the current marker to be an average of it and the provided marker.

    # Start our list of unique markers with the first one only.
    unique_markers = [markers[0]]

    # Check the rest of the list.
    for marker in markers[1:]:
        for unique_marker in unique_markers:
            if unique_marker.is_close(marker, tolerance):
                unique_marker.average_with(marker)
                break
            else:
                # If we didn't find a match, add this marker to our list of unique markers
                unique_markers.append(marker)

    return unique_markers

class ptz_class():
    def __init__(self, cam):
        self.cap = cam#IpVideoCapture(f'rtsp://{ID}:{PASSWORD}@{ONVIF_URL}:554/0/onvif/profile1/media.smp')

        self.ARUCO_PARAMETERS = cv2.aruco.DetectorParameters()
        self.ARUCO_DICT_6X6 = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)

        self.is_run = False

    def qr_detection(self,img):
        result = []
        print('aaa1')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, self.ARUCO_DICT_6X6, parameters=self.ARUCO_PARAMETERS)
        result.append((corners,ids,rejectedImgPoints))
        all_markers = []

        print('aaa2')
        for num in range(11, 255, 80):
            ret, gray_thr = cv2.threshold(gray, num, 255, cv2.THRESH_BINARY)
            corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray_thr, self.ARUCO_DICT_6X6, parameters=self.ARUCO_PARAMETERS)
            if not (ids is None or corners is None):
                markers = [ArucoMarker(id[0], corner[0]) for id, corner in zip(ids, corners)]
                for marker in markers:
                    all_markers.append(marker)

            gray_adm = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, num, 2)
            corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray_adm, self.ARUCO_DICT_6X6, parameters=self.ARUCO_PARAMETERS)
            if not (ids is None or corners is None):
                markers = [ArucoMarker(id[0], corner[0]) for id, corner in zip(ids, corners)]
                for marker in markers:
                    all_markers.append(marker)

            gray_adg = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, num, 2)
            corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray_adg, self.ARUCO_DICT_6X6, parameters=self.ARUCO_PARAMETERS)
            if not (ids is None or corners is None):
                markers = [ArucoMarker(id[0], corner[0]) for id, corner in zip(ids, corners)]
                for marker in markers:
                    all_markers.append(marker)

        ret, gray_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray_otsu, self.ARUCO_DICT_6X6, parameters=self.ARUCO_PARAMETERS)
        if not (ids is None or corners is None):
            markers = [ArucoMarker(id[0], corner[0]) for id, corner in zip(ids, corners)]
            for marker in markers:
                all_markers.append(marker)
        if len(all_markers)!=0:
            all_markers = unique_markers(all_markers,tolerance=10)
        return all_markers

def generate_and_save_ar_code(marker_id):
    # ArUco dictionary and parameters
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
    parameters= cv2.aruco.DetectorParameters()
    # Generate a random ArUco marker

    marker_size = 10000
    marker_image = np.zeros((marker_size, marker_size), dtype=np.uint8)
    marker = cv2.aruco.generateImageMarker(dictionary=aruco_dict, id=marker_id, sidePixels=marker_size, img=marker_image)
    #print(marker_id,marker.shape)
    # Save the marker as an image
    cv2.imwrite(f'{marker_id}.png',marker)
    marker = cv2.cvtColor(marker,cv2.COLOR_GRAY2BGR)
    return marker


if __name__ == "__main__":
    generate_and_save_ar_code(100)
    generate_and_save_ar_code(200)