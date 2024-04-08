# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
import cv2
import threading
import base64
# import picamera2
import time
import numpy as np

from multiprocessing import Pipe
from src.utils.messages.allMessages import (
    mainCamera,
    serialCamera,
    Recording,
    Record,
    Config,
    LaneCamera,
    ObjectCamera,
)
from src.templates.threadwithstop import ThreadWithStop


class threadCamera(ThreadWithStop):
    """Thread which will handle camera functionalities.\n
    Args:
        pipeRecv (multiprocessing.queues.Pipe): A pipe where we can receive configs for camera. We will read from this pipe.
        pipeSend (multiprocessing.queues.Pipe): A pipe where we can write configs for camera. Process Gateway will write on this pipe.
        queuesList (dictionar of multiprocessing.queues.Queue): Dictionar of queues where the ID is the type of messages.
        logger (logging object): Made for debugging.
        debugger (bool): A flag for debugging.
    """

    # ================================ INIT ===============================================
    def __init__(self, pipeRecv, pipeSend, queuesList, logger, debugger, period):
        super(threadCamera, self).__init__()
        self.queuesList = queuesList
        self.logger = logger
        self.pipeRecvConfig = pipeRecv
        self.pipeSendConfig = pipeSend
        self.debugger = debugger
        self.cam_period = period
        self.frame_rate = 5
        self.recording = False
        pipeRecvRecord, pipeSendRecord = Pipe(duplex=False)
        self.pipeRecvRecord = pipeRecvRecord
        self.pipeSendRecord = pipeSendRecord
        self.video_writer = ""
        # self.Timer1 = threading.Timer(1,self.Queue_Sending)
        # self.Timer2 = threading.Timer(0.3,self.Timer_camera_callback)
        self.enable_publish = False
        self.subscribe()
        self._init_camera()
        self.Queue_Sending()
        self.Timer_camera_callback()
        self.Configs()
        self.cnt = 0

        
    def subscribe(self):
        """Subscribe function. In this function we make all the required subscribe to process gateway"""
        self.queuesList["Config"].put(
            {
                "Subscribe/Unsubscribe": "subscribe",
                "Owner": Record.Owner.value,
                "msgID": Record.msgID.value,
                "To": {"receiver": "threadCamera", "pipe": self.pipeSendRecord},
            }
        )
        self.queuesList["Config"].put(
            {
                "Subscribe/Unsubscribe": "subscribe",
                "Owner": Config.Owner.value,
                "msgID": Config.msgID.value,
                "To": {"receiver": "threadCamera", "pipe": self.pipeSendConfig},
            }
        )
    
    def Timer_camera_callback(self):
        self.enable_publish = True
        threading.Timer(self.cam_period,self.Timer_camera_callback).start()
    
    def Queue_Sending(self):
        """Callback function for recording flag."""
        self.queuesList[Recording.Queue.value].put(
            {
                "Owner": Recording.Owner.value,
                "msgID": Recording.msgID.value,
                "msgType": Recording.msgType.value,
                "msgValue": self.recording,
            }
        )
        threading.Timer(1,self.Queue_Sending).start()

    # =============================== STOP ================================================
    def stop(self):
        if self.recording:
            self.video_writer.release()
        super(threadCamera, self).stop()
        self.camera.release()

    # =============================== CONFIG ==============================================
    def Configs(self):
        """Callback function for receiving configs on the pipe."""
        while self.pipeRecvConfig.poll():
            message = self.pipeRecvConfig.recv()
            message = message["value"]
            print(message)
            self.camera.set_controls(
                {
                    "AeEnable": False,
                    "AwbEnable": False,
                    message["action"]: float(message["value"]),
                }
            )
        threading.Timer(1, self.Configs).start()

    # ================================ RUN ================================================
    def run(self):
        """This function will run while the running flag is True. It captures the image from camera and make the required modifies and then it send the data to process gateway."""
        var = True
        temp = 0
        while self._running:
            try:
                if self.pipeRecvRecord.poll():
                    msg = self.pipeRecvRecord.recv()
                    self.recording = msg["value"]
                    if msg["value"] == False:
                        self.video_writer.release()
                    else:
                        fourcc = cv2.VideoWriter_fourcc(
                            *"MJPG"
                        )  # You can choose different codecs, e.g., 'MJPG', 'XVID', 'H264', etc.
                        self.video_writer = cv2.VideoWriter(
                            "output_video" + str(time.time()) + ".avi",
                            fourcc,
                            self.frame_rate,
                            (2048, 1080),
                        )
            except Exception as e:
                print(e)
            if self.debugger == True:
                self.logger.warning("getting image")
            
            # =================================== Read camera frame ============================
            if self.camera.isOpened():
                self.frame_cnt += 1
                frame = self.camera.read()[1]

                if self.enable_publish:
                    frame = cv2.resize(frame,(640,360))                                 ###   change cam width      
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    request = frame
                    if var:
                        if self.recording == True:
                            cv2_image = cv2.cvtColor(request, cv2.COLOR_RGB2BGR)
                            self.video_writer.write(cv2_image)
                        request2 = frame
                        #request2 = self.cnt
                        # request2 = request2[:360, :]
                        # cv2.('raw-frame.jpg',request)
                        

                        # image_data_encoded = f"{self.cnt}"
                        
                        request2 = cv2.cvtColor(request2, cv2.COLOR_RGB2BGR)
                        if temp == 0:
                             cv2.imwrite('raw-frame-from-CAM.jpg',request2)
                             print("Saved raw-frame-from-CAM")
                             temp = 1                

                        print(f"Camera pushed a frame {request2[0][0]}")
                        self.cnt += 1
                        if self.cnt >=256:
                            self.cnt = 0

                        self.queuesList[LaneCamera.Queue.value].put(
                            {
                                "Owner": LaneCamera.Owner.value,
                                "msgID": LaneCamera.msgID.value,
                                "msgType": LaneCamera.msgType.value,
                                "msgValue": request2,
                            }
                        )
                        self.queuesList[ObjectCamera.Queue.value].put(
                            {
                                "Owner": ObjectCamera.Owner.value,
                                "msgID": ObjectCamera.msgID.value,
                                "msgType": ObjectCamera.msgType.value,
                                "msgValue": request2,
                            }
                        )
                    self.enable_publish = False
            else:
                print("Error: Could not open webcam.")
                break
            # ==================================================================================
            

            

    # =============================== START ===============================================
    def start(self):
        super(threadCamera, self).start()

    # ================================ INIT CAMERA ========================================
    
    def _init_camera(self):
        """This function will initialize the camera object. It will make this camera object have two chanels "lore" and "main"."""
        # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
        self.camera = cv2.VideoCapture(0)
        # self.camera = cv2.VideoCapture("src/hardware/camera/threads/bfmc2020_online_2.avi")
        # Set the video resolution (optional)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)                            ###   change cam width 
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.frame_cnt = 0
        
