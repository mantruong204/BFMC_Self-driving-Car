# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC orginazers
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
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# ===================================== GENERAL IMPORTS ==================================
import sys

import base64
import numpy as np
import cv2

sys.path.append(".")
from multiprocessing import Queue, Event
import logging


# ===================================== PROCESS IMPORTS ==================================
from src.gateway.processGateway import processGateway
from src.hardware.camera.processCamera import processCamera
from src.hardware.serialhandler.processSerialHandler import processSerialHandler
from src.Detection.processDetection import processDetection
from src.utils.PCcommunicationDemo.processPCcommunication import (
    processPCCommunicationDemo,
)
from src.utils.PCcommunicationDashBoard.processPCcommunication import (
    processPCCommunicationDashBoard,
)
from src.data.CarsAndSemaphores.processCarsAndSemaphores import processCarsAndSemaphores
from src.data.TrafficCommunication.processTrafficCommunication import (
    processTrafficCommunication,
)
from src.Detection.threads.ObjDetect.Object_Detect import RunAIThread
from src.utils.messages.allMessages import ObjectTh
# ======================================== SETTING UP ====================================
allProcesses = list()
queueList = {
    "Critical": Queue(),
    "Warning": Queue(),
    "General": Queue(),
    "Config": Queue(),
    "Detection": Queue(),
    "LaneCamera": Queue(),
    "ObjectCamera": Queue(),
}

logging = logging.getLogger()

TrafficCommunication = False
Camera = True
PCCommunicationDemo = True
CarsAndSemaphores = False
SerialHandler = True
Detection = True
AI_Enable = True

# ========================================================================================
if AI_Enable:
    print("____Preparing AI____\n")
    AI_process = RunAIThread()
    print("____MAIN Prepared AI DONE____\n", AI_process)

# ===================================== SETUP PROCESSES ==================================

# Initializing gateway
processGateway = processGateway(queueList, logging)
allProcesses.append(processGateway)

# Initializing camera
if Camera:
    processCamera = processCamera(queueList, logging)
    allProcesses.append(processCamera)

# Initializing interface
if PCCommunicationDemo:
    processPCCommunication = processPCCommunicationDemo(queueList, logging)
    allProcesses.append(processPCCommunication)
else:
    processPCCommunicationDashBoard = processPCCommunicationDashBoard(
        queueList, logging
    )
    allProcesses.append(processPCCommunicationDashBoard)

# Initializing cars&sems
if CarsAndSemaphores:
    processCarsAndSemaphores = processCarsAndSemaphores(queueList)
    allProcesses.append(processCarsAndSemaphores)

# Initializing GPS
if TrafficCommunication:
    processTrafficCommunication = processTrafficCommunication(queueList, logging, 3)
    allProcesses.append(processTrafficCommunication)

# Initializing serial connection NUCLEO - > PI
if SerialHandler:
    processSerialHandler = processSerialHandler(queueList, logging)
    allProcesses.append(processSerialHandler)

# Initalizing Detection process
if Detection:
    processDetection = processDetection(queueList, logging)
    allProcesses.append(processDetection)
# ===================================== START PROCESSES ==================================
for process in allProcesses:
    process.daemon = True
    process.start()

# ===================================== STAYING ALIVE ====================================
temp = 0
blocker = Event()

while True:
    try:
        if AI_Enable:                    
            msg = None
            #print("Hello")
            if not queueList["ObjectCamera"].empty():
                msg = queueList["ObjectCamera"].get()
                img = msg["msgValue"]

                #img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                if temp == 0:
                    cv2.imwrite("img_recv_by_OBJECT.jpg",img)
                    temp = 1
                print(f"Object received a frame {img[0][0]}")
                object_data = AI_process.process(img)
                print(f"\n\nresult = {object_data}")
                
                queueList[ObjectTh.Queue.value].put(
                    {
                            "Owner": ObjectTh.Owner.value,
                            "msgID": ObjectTh.msgID.value,
                            "msgType": ObjectTh.msgType.value,
                            "msgValue": object_data,
                    }
                )
                print("~~~~~~AI put a result to :",ObjectTh.Queue.value,"~~~~~\n")
    except KeyboardInterrupt:
        print("\nCatching a KeyboardInterruption exception! Shutdown all processes.\n")
        for proc in allProcesses:
            print("Process stopped", proc)
            proc.stop()
            proc.join()

