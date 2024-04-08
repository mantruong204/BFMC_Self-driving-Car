import cv2
import threading
import base64
import numpy as np
# import picamera2
import time
from multiprocessing import Pipe
from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (
    LaneTh,
    ObjectTh,
    SpeedMotor,
    SteerMotor,
    ResultCamera,
)
import threading

class threadCameraDecision(ThreadWithStop):
    def __init__(self, queues, logging, debugger):
        super(threadCameraDecision, self).__init__()
        self.queueList = queues
        self.logging = logging
        self.debugging = debugger

        self.lane_data_flag = False
        self.lane_speed = 0.0
        self.lane_angle = 0.0
        self.lane_img = []

        self.obj_data_flag = False
        self.obj_bbox = (0.0 , 0.0 , 0.0 , 0.0)
        self.obj_class = ""
        self.obj_conf = 0

        self.light = {}
        self.sign = {}
        self.obj = {}

        self.status = None
        self.angle_value_array = []        
        
        
    def thread_initilaize(self):
        threading.Timer(1, self.thread_initilaize).start()


    # Send setpoint functionality
    def output_publish (self,speed,angle):
       self.queueList[SpeedMotor.Queue.value].put(
       {
                            "Owner": SpeedMotor.Owner.value,
                            "msgID": SpeedMotor.msgID.value,
                            "msgType": SpeedMotor.msgType.value,
                            "msgValue": speed,
       }
       )
       self.queueList[SteerMotor.Queue.value].put(
       {
                            "Owner": SteerMotor.Owner.value,
                            "msgID": SteerMotor.msgID.value,
                            "msgType": SteerMotor.msgType.value,
                            "msgValue": angle,
       }
       )
       #print("________Published SETPOINTS_________")

    def display_objs (self,img,light,sign,obj):
        font_size = 1.0
        thickness = 2
        if not light["class"] == 'none':
            cv2.rectangle(img,
(int(light["box"][0]),int(light["box"][1])),
(int(light["box"][2]),int(light["box"][3])),
(0,165,255),
thickness)
            label = "{}:{:.2f}".format(light["class"],light["conf"])
            cv2.putText(img,label,(int(light["box"][0]*0.8),int(light["box"][1])),cv2.FONT_HERSHEY_DUPLEX,font_size,(0,165,255),thickness)
            """
            #Debug
            x = int((light["box"][0] + light["box"][2])/2)
            y = int((light["box"][1] + light["box"][3])/2)
            print("+++++++++Color light++++++++++++", img[x][y])
            """

        if not sign["class"] == 'none':
            cv2.rectangle(img,
(int(sign["box"][0]),int(sign["box"][1])),
(int(sign["box"][2]),int(sign["box"][3])),
(0,165,255),
thickness)
            label = "{}:{:.2f}".format(sign["class"],sign["conf"])
            cv2.putText(img,label,(int(sign["box"][0]*0.8),int(sign["box"][1])),cv2.FONT_HERSHEY_DUPLEX,font_size,(0,165,255),thickness)

        if not obj["class"] == 'none':
            cv2.rectangle(img,
(int(obj["box"][0]),int(obj["box"][1])),
(int(obj["box"][2]),int(obj["box"][3])),
(0,165,255),
thickness)
            label = "{}:{:.2f}".format(obj["class"],obj["conf"])
            cv2.putText(img,label,(int(obj["box"][0]*0.8),int(obj["box"][1])),cv2.FONT_HERSHEY_DUPLEX,font_size,(0,165,255),thickness)


        """
        light_str = "TF Light = " + str(light)
        light_str_clr = (0,0,255)
        cv2.putText(img,str(light_str),(20,begin_row+row_step*5),cv2.FONT_HERSHEY_DUPLEX,font_size,light_str_clr,thickness)

        sign_str = "TF Sign = " + str(sign)
        sign_str_clr = (0,0,255)
        cv2.putText(img,str(sign_str),(20,begin_row+row_step*6),cv2.FONT_HERSHEY_DUPLEX,font_size,sign_str_clr,thickness)

        obj_str = "Objects = " + str(obj)
        obj_str_clr = (0,0,255)
        cv2.putText(img,str(obj_str),(20,begin_row+row_step*7),cv2.FONT_HERSHEY_DUPLEX,font_size,obj_str_clr,thickness)
        """
    # ================================ RUN ================================================
    def run(self):
        while self._running:
            msg = None
            if not self.queueList["Detection"].empty():
                #print("________DecisionTh got DATA_________")
                msg = self.queueList["Detection"].get()
                Owner = msg["Owner"]
                Value = msg["msgValue"]

                if Owner == LaneTh.Owner.value:
                    # print("~~~~~~~~~~~~Decision got LANE data~~~~~~~~~\n")
                    self.lane_speed = Value["Speed"]*0.4
                    self.lane_angle = Value["Angle"]
                    self.lane_img   = Value["Lane_img"]
                    self.lane_data_flag = True

                if Owner == ObjectTh.Owner.value:
                    # print("~~~~~~~~~~~~Decision got OBJ data~~~~~~~~~\n")
                    self.light = Value["light_color"]
                    self.sign = Value["sign_type"]
                    self.obj = Value["object"]

                    self.obj_light = Value["light_color"]["class"]
                    self.obj_sign = Value["sign_type"]["class"]
                    self.obj_obj = Value["object"]["class"]

                    self.obj_data_flag = True

            if self.lane_data_flag and self.obj_data_flag:
                img = self.lane_img
                # print(f"Decision received a frame {img[0][0]}")
                print('+++++++++++++++++++++++++++++++++++++++++++',self.status)
                set_speed = self.lane_speed     # SPEED setpoint will be sent to embedded
                set_angle = self.lane_angle     # STEERING ANGLE setpoint will be sent to embedded
                
                # self.angle_value_array.append(self.lane_angle)
                # if len(self.angle_value_array) > 5:
                #     self.angle_value_array.pop(0)
                # Calibration
                # # angle = k*set + offset
                # if set_angle > 0:
                #     set_angle *= 0.6971     #Xu huong tang goc duong
                # else:
                #     set_angle *= 1.3029     #Giam goc am
                # set_angle += 5.15
                
                # Upper limit
                if set_angle > 25:
                    set_angle = 25
                elif set_angle < -25:
                    set_angle = -25


                    
                #Draw light, sign, obj atop lane_img
                #TODO

                self.display_objs(img,self.light,self.sign,self.obj)

                #Decision making - Le Thai Tan
                #TODO
                # print("Light: ",self.obj_light)
                # print("Sign : ",self.obj_sign)
                # print("Objs : ",self.obj_obj)
                if self.status == None:
                    #--------------------------------ONlY Traffic_Light----------------------------------
                    if self.obj_light == "none" and self.obj_sign == "none" and self.obj_obj == "none":
                        self.output_publish(set_speed,set_angle)
                    elif self.obj_light == "red" and self.obj_sign == "none" and self.obj_obj == "none":
                        self.status = 'red'
                        threading.Thread(target=self.red).start()
                    elif self.obj_light == "yellow" and self.obj_sign == "none" and self.obj_obj == "none":
                        self.output_publish(set_speed*0.7,set_angle)
                    elif self.obj_light == "green" and self.obj_sign == "none" and self.obj_obj == "none":
                        self.status = 'green'
                        threading.Thread(target=self.green).start()
                    #---------------------------------ONLY Traffic sign----------------------------------
                    elif self.obj_light == "none" and self.obj_sign == "stop" and self.obj_obj == "none":
                        self.status = "stop" 
                        print("________________________________________stop________________________")                       
                        threading.Thread(target=self.Stop_thread).start()
                        
                    elif self.obj_light == "none" and self.obj_sign == "crosswalk" and self.obj_obj == "none":
                        self.output_publish(set_speed*0.7,set_angle)
                        if self.obj_obj == 'person':
                            self.output_publish(0,set_angle)

                    elif self.obj_light == "none" and self.obj_sign == "priority" and self.obj_obj == "none":
                        #TODO: TURN RIGHT => Priority Thread
                        self.status = "priority"
                        threading.Thread(target=self.priority).start()
                    elif self.obj_light == "none" and self.obj_sign == "noentry" and self.obj_obj == "none":
                        #TODO
                        self.output_publish(set_speed,set_angle)
    
                    elif self.obj_light == "none" and self.obj_sign == "oneway" and self.obj_obj == "none":
                        #TODO
                        self.output_publish(set_speed,set_angle)
                    elif self.obj_light == "none" and self.obj_sign == "endHighway" and self.obj_obj == "none":
                        #TODO
                        self.output_publish(set_speed,set_angle)
                    elif self.obj_light == "none" and self.obj_sign == "enterHighway" and self.obj_obj == "none":
                        #TODO
                        self.status = 'enterHightway'

                        threading.Thread(target=self.enterHightway).start()
                    elif self.obj_light == "none" and self.obj_sign == "roundAbout" and self.obj_obj == "none":
                        #TODO: Turn LEFT => Roundabout Thread
                        self.status = 'Roundabout'
                        threading.Thread(target=self.Roundabout).start()
                        

                    #------------------------------------ PARKING ----------------------------------------
                    elif self.obj_light == "none" and self.obj_sign == "parking" and self.obj_obj == "none":
                        self.status = "parking"                        
                        threading.Thread(target=self.Parking_thread).start()
                    
                    #PEDESTRIAN
                    elif self.obj_obj == "person":
                        self.status ="person_nosign"
                        threading.Thread(target=self.Person_thread).start()
                    #OVERTAKE
                    elif self.obj_obj == "car":
                        self.status = "overtake"
                        threading.Thread(target=self.overtake).start()
                    #TODO


                    

                #Encode img before sending to Demo
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                result_img = img
                result_img = cv2.resize(result_img,(480,360))
                _, encoded_img = cv2.imencode(".jpg", result_img)
                image_data_encoded = base64.b64encode(encoded_img).decode("utf-8")


                # Publish result frame
                self.queueList[ResultCamera.Queue.value].put(
                    {
                        "Owner": ResultCamera.Owner.value,
                        "msgID": ResultCamera.msgID.value,
                        "msgType": ResultCamera.msgType.value,
                        "msgValue": image_data_encoded,
                    }
                )
                self.lane_data_flag = False
                self.obj_data_flag = False
                print("\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    # ==================================== START =========================================
    def start(self):
        super(threadCameraDecision, self).start()

    # ==================================== STOP ==========================================
    def stop(self):
        """This function will close the thread and will stop the car."""
        super(threadCameraDecision, self).stop()

    # =================================Define thread that process task====================
    def Stop_thread(self):
        self.output_publish(0,0)
        time.sleep(3)
        for i in range(3):
            self.output_publish(self.lane_speed,-16)
            time.sleep(0.4)
        # self.output_publish(20,self.lane_angle)
        # time.sleep(0.5)
        # self.output_publish(20,)
        # time.sleep(2)
        self.status = None
    def overtake(self):
        self.output_publish(20,0)
        time.sleep(0.5)
        self.output_publish(20,-20)
        time.sleep(1.2)
        self.output_publish(40,22)
        time.sleep(1.5)
        self.output_publish(40,12)
        time.sleep(0.5)
        self.output_publish(30,22)
        time.sleep(0.3)
        self.output_publish(20,-10)
        time.sleep(0.5)
        self.status = None
    def Parking_thread(self):
        # --------------Define what car need to do with parking sign--------------#
        # TODO
        # LE THAI TAN
        # Parking
        # self.output_publish(10,-5)
        # time.sleep(0.5)
        for i in range(14):
            self.output_publish(self.lane_speed,self.lane_angle)
            # self.output_publish(20,self.lane_angle)
            time.sleep(0.4)
        # for i in range(3):
        #     self.output_publish(40,0)
        #     time.sleep(0.5)
        # self.output_publish(40,self.lane_angle+1)
        # time.sleep(0.2)
        # self.output_publish(40,self.lane_angle)
        # time.sleep(2.8)
            
        # self.output_publish(0,0)
        # time.sleep(3)
        
        self.output_publish(self.lane_speed,-20)
        time.sleep(1.5)
        self.output_publish(0,0)
        time.sleep(1)
        self.output_publish(-30,25)
        time.sleep(1)
        self.output_publish(-20,-25)
        time.sleep(3.4)
        self.output_publish(0,0)
        time.sleep(0.2)
        self.output_publish(20,0)
        time.sleep(1)
        self.output_publish(0,0)
        time.sleep(0.5)
        self.output_publish(0,0)
        time.sleep(1)
        self.output_publish(-20,0)
        time.sleep(1.2)
        # out parking
        self.output_publish(20,-25)
        time.sleep(1.7)
        self.output_publish(20,25)
        time.sleep(2.4)
        self.output_publish(20,-10)
        time.sleep(0.5)
        # self.output_publish(20,10)
        # time.sleep(1)
        # self.output_publish(0,0)
        # time.sleep(1)
        self.status = None
    
    def Roundabout(self):
        self.output_publish(20,7)
        time.sleep(0.7)
        self.output_publish(20,0)
        time.sleep(1)
        # self.output_publish(20,-20)
        # time.sleep(1)
        for i in range (14):
            self.output_publish(self.lane_speed,-19)
            time.sleep(0.4)
        self.output_publish(10,10)
        time.sleep(0.5)
        self.status = None
    def Person_thread(self):
        self.output_publish(0,0)
        time.sleep(3)
        self.status= None
        
        self.status = None
    def priority(self):
        self.output_publish(20,0)
        time.sleep(1)
        self.output_publish(20,25)
        time.sleep(1)
        for i in range (5):
            self.output_publish(20,22)
            time.sleep(0.4)
        self.status = None
    def green(self):
        self.output_publish(20,self.lane_angle)
        time.sleep(3)
        for i in range (5):
            self.output_publish(20,25)
            time.sleep(0.4)
        self.status = None
    def red(self):
        # if self.red == 0:
        #     for i in range(2):
        #         self.output_publish(20,self.lane_angle)
        #         time.sleep(0.4)
        #     self.red = 1
        self.output_publish(0,0)
        time.sleep(1.5)
        self.status = None

    def enterHightway(self):
        self.output_publish(self.lane_speed,-10)
        time.sleep(0.5)
        while self.obj_sign != 'endHighway':
            # print('================',self.obj_obj)
            self.output_publish(self.lane_speed*1.3,self.lane_angle)
            time.sleep(0.4)
        self.status = None