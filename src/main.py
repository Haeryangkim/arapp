import cv2
from ptz_qrdetection import ptz_class, IpVideoCapture, ArucoMarker
import argparse

# from ardetector import ArucoMarker

def start_ar_system(cap, outport, target_id, base_size):
    detector = ptz_class(cap)
    is_stream = False
    if is_stream:
        import gi
        gi.require_version('Gst', '1.0')
        gi.require_version('GstRtspServer', '1.0')
        from gi.repository import Gst, GObject
        import rtsp
        from threading import Thread

        GObject.threads_init()
        Gst.init(None)
        server = rtsp.GstServer('admin', '4321', sub_dir='/stream', port=outport)
        Thread(target=GObject.MainLoop().run).start()

    print("#System Start")

    while True:
        ret, frame = cap.read()
        view_img = frame
        reses = detector.qr_detection(frame)

        for res in reses:
            view_img = res.draw_corner(view_img)

        for res in reses:
            size = check_depth(res, target_id, base_size)
            if size < 3:
                res.draw_side_line(view_img, (0, 0, 255))
            elif size > 3:
                res.draw_side_line(view_img, (0, 255, 0))

        if is_stream:
            server.set_img(view_img)
        else:
            cv2.imshow("TEST", view_img)
            cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()


def check_depth(arclass: ArucoMarker, target_id, base_pixel) -> float:
    print(f"ID : {arclass.id}, Pixel Size : {arclass.calculate_average_length()}")
    if arclass.id == target_id:
        return base_pixel / arclass.calculate_average_length()
    else:
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start AR system with specified parameters')
    parser.add_argument('--rtsp_path', type=str, default='rtsp://admin:1q2w3e4r5t!@192.168.0.64:554/0/onvif/profile2/media.smp', help='RTSP path for video capture')
    parser.add_argument('--outport', type=int, default=8554, help='Output port number')
    parser.add_argument('--target_id', type=int, default=1, help='Target ID')
    parser.add_argument('--base_size', type=int, default=100, help='Base size')

    args = parser.parse_args()

    rtsp_path = args.rtsp_path
    outport = args.outport
    target_id = args.target_id
    base_size = args.base_size
    _p = 'rtsp://admin:1q2w3e4r5t!@192.168.0.64:554/0/onvif/profile2/media.smp'
    cap = IpVideoCapture(_p)
    start_ar_system(cap, outport, target_id, base_size)
