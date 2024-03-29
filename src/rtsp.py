import cv2
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject
import threading
import socket


def get_ip_address(ifname):
    return socket.gethostbyname(socket.getfqdn())

class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **properties):
        super(SensorFactory, self).__init__(**properties)
        self.number_frames = 0
        self.fps = 10
        self.duration = 1. / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        self.width = 1920
        self.height = 1080
        self.launch_string = (f'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME caps=video/x-raw,'
                              f'format=BGR,width={self.width},height={self.height} ! '
                              f'videoconvert ! video/x-raw,format=I420 ! x264enc speed-preset=ultrafast '
                              f'tune=zerolatency ! rtph264pay config-interval=1 name=pay0 pt=96')

        self.img = None

    def on_need_data(self, src,length):
        if True:
            ret = True
            frame = self.img.copy()
            # ret , frame = self.cap.read()
            if ret:
                data = frame.tostring()
                buf = Gst.Buffer.new_allocate(None, len(data), None)
                buf.fill(0, data)
                buf.duration = self.duration
                timestamp = self.number_frames * self.duration
                buf.pts = buf.dts = int(timestamp)
                buf.offset = timestamp
                self.number_frames += 1
                retval = src.emit('push-buffer', buf)

                # print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames,
                # self.duration, self.duration / Gst.SECOND))

                if retval != Gst.FlowReturn.OK:
                    print(retval)

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)
        print('#Connected')

    def set_img(self, img):
        img = cv2.resize(img, (self.width, self.height))
        self.img = img


class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, outid, password, sub_dir, port):
        GObject.threads_init()
        Gst.init(None)
        # super(GstServer, self).__init__(**properties)
        self.factory = SensorFactory()
        self.factory.set_shared(True)
        server = GstRtspServer.RTSPServer()
        server.get_mount_points().add_factory(sub_dir, self.factory)
        server.set_service(str(port))

        auth = GstRtspServer.RTSPAuth()
        token = GstRtspServer.RTSPToken()

        token.set_string('media.factory.role', outid)
        basic = GstRtspServer.RTSPAuth.make_basic(outid, password)
        auth.add_basic(basic, token)
        server.set_auth(auth)

        permissions = GstRtspServer.RTSPPermissions()
        permissions.add_permission_for_role(outid, "media.factory.access", True)
        permissions.add_permission_for_role(outid, "media.factory.construct", True)

        self.factory.set_permissions(permissions)
        server.attach(None)
        cur_ip = get_ip_address('enp2s0')
        #print("#RTSP Server up")
        print('#Gst Server: rtsp://{}:[Specified_Port]{}'.format(cur_ip, sub_dir))

    def run(self):
        loop = GObject.MainLoop()
        t = threading.Thread(target=loop.run)
        t.daemon = True
        t.start()

    def set_img(self, img):
        self.factory.set_img(img)


def loop():
    loop = GObject.MainLoop()
    loop.run()



def init():
    GObject.threads_init()
    Gst.init(None)


if __name__ == '__main__':
    init()

    server = GstServer('admin', '4321', sub_dir='/origin', port=8554)
    # server = GstServer(sub_dir='/origin',port = 8555)

    loop()
