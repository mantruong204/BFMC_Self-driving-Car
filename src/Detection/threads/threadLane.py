import threading
import base64
import cv2
import numpy as np
from multiprocessing import Pipe
from src.templates.threadwithstop import ThreadWithStop
import threading
import time

from src.Detection.threads.LaneDetect import config

from src.utils.messages.allMessages import  LaneTh
from src.Detection.threads.LaneDetect.Lane_Detection import Lane_Detect_process

class threadLane(ThreadWithStop):
    def __init__(self, queues, logging, debugger):
        super(threadLane, self).__init__()
        self.queueList = queues
        self.logging = logging
        self.debugging = debugger
        self.temp = 0
        self.angle = 0
        self.speed = 0
        self.result_img = np.zeros((640,360,3), dtype=np.uint8)
        self.lane_done = False


    # ================================ RUN ================================================
    def run(self):
        while self._running:
            try:
                
                msg = None
                if not self.queueList["LaneCamera"].empty():
                    # start = time.time()
                    msg = self.queueList["LaneCamera"].get()
                    img = msg["msgValue"]
                    # print(f"Lane received a frame {img}")


                    print(f"Lane received a frame {img[0][0]}")

                    if self.temp == 0:
                        cv2.imwrite('frame-received-by-LANE.jpg',img)
                        print("Saved frame-received-by-LANE")
                        self.temp = 1
                    

                    #Detection
                    # thread_detect = threading.Thread(target=self.lane_detect(img))
                    # thread_detect.start()
                    # thread_detect.join(timeout=0.4)

                    timer = threading.Timer(0, self.lane_detect,args=(img,))
                    self.lane_done = False

                    # print("     self.lane_done ****:    ",self.lane_done)

                    timer.start()
                    time.sleep(0.35)
                    timer.cancel()
                    # del timer

                    # print("     self.lane_done:    ",self.lane_done)

                    if not self.lane_done:
                        print("____Exit LANE before done___") 
                        self.speed *= 0.85
                    
                        begin_row = 30
                        row_step = 30
                        font_size = 1.0
                        thickness = 2
                        cv2.putText(self.result_img,"Time out",(20,begin_row+row_step*5),cv2.FONT_HERSHEY_DUPLEX,font_size,(255,255,255),thickness)

                        #self.angle = 0.0



                    #self.result_img = cv2.cvtColor(self.result_img, cv2.COLOR_RGB2BGR)



                    # print(f"speed: {self.speed}, \nangle: {self.angle}")
                    # print(" ")
                    # cv2.imshow("Result image", result_img)

                    lane_output_data = {'Speed': self.speed, 'Angle': self.angle, 'Lane_img' : self.result_img}
                    self.queueList[LaneTh.Queue.value].put(
                        {
                            "Owner": LaneTh.Owner.value,
                            "msgID": LaneTh.msgID.value,
                            "msgType": LaneTh.msgType.value,
                            "msgValue": lane_output_data,
                        }
                    )       
                    print("~~~~~~~LANEThread put a result to : ",LaneTh.Queue.value,"~~~~~\n")
                    # end = time.time()
                    # print(f"LaneTh_time = {end - start}")
            except Exception as e:
                print(e)

    # ==================================== START =========================================
    def start(self):
        super(threadLane, self).start()

    # ==================================== STOP ==========================================
    def stop(self):
        """This function will close the thread and will stop the car."""
        super(threadLane, self).stop()
    def lane_detect(self, img):
        # print("========== Entering Lane ..........................")
        self.angle, self.speed, self.result_img = Lane_Detect_process(img)
        self.lane_done = True
