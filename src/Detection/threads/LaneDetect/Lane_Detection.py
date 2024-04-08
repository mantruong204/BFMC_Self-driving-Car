
import cv2
from collections import deque
from numpy import interp
from src.Detection.threads.LaneDetect import config
# ****************************************************  DETECTION ****************************************************
# ****************************************************    LANES   ****************************************************

# >>>>>>>>>>>>>>>>>>>>>>>> STAGE 1 [IMPORTS] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
from src.Detection.threads.LaneDetect.Segmentation import Segment

# >>>>>>>>>>>>>>>>>>>>>>>> STAGE 2 [IMPORTS] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
from src.Detection.threads.LaneDetect.EstimationAlgo import Estimate_Lane

# >>>>>>>>>>>>>>>>>>>>>>>> STAGE 4 [IMPORTS] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
from src.Detection.threads.LaneDetect.GetStateInfoandDisplayLane import FetchInfoAndDisplay




def detect_Lane(img):
        """ Extract required data from the lane lines representing road lane boundaries.

        Args:
                img (numpy nd array): Prius front-cam view

        Returns:
                distance    (int): car_front <===distance===> ideal position on road 
                curvature (angle): car <===angle===> roads_direction
                                e.g. car approaching a right turn so road direction is around or less then 45 deg
                                                                                cars direction is straight so it is around 90 deg
        """          
        # >>>>>>>>>>>>>>>>>>>>>>>> Optimization No 2 [CROPPING] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        img_cropped = img

        # [Lane Detection] STAGE_1 (Segmentation) <<<<<<--->>>>>> [EDGE]:
        Mid_edge_ROI,Mid_ROI_mask,Out_edge_ROI,Out_ROI_mask,Zebra_cross,Intersection_status = Segment(img_cropped)
       
        # [Lane Detection] STAGE_2 (Estimation) <<<<<<--->>>>>> [Connect seperate line marks]:
        Estimated_midlane = Estimate_Lane(Mid_edge_ROI,config.MaxDist_resized)
        Estimated_OUTlane = Estimate_Lane(Out_ROI_mask,config.MaxDist_resized)

        # [Lane Detection] STAGE_3 (Data_Extraction) <<<<<<--->>>>>> :
        Distance , Curvature = FetchInfoAndDisplay(Mid_edge_ROI,Estimated_midlane,Estimated_OUTlane,img_cropped,0)

        return Distance,Curvature,Zebra_cross, Intersection_status

def follow_Lane(Max_Sane_dist,distance,curvature):

        car_speed = 50


        
        Max_turn_angle_neg = -25
        Max_turn_angle = 25

        CarTurn_angle = 0

        if( (distance > Max_Sane_dist) or (distance < (-1 * Max_Sane_dist) ) ):
            # Max sane distance reached ---> Max penalize (Max turn Tires)
            if(distance > Max_Sane_dist):
                #Car offseted left --> Turn full wheels right
                CarTurn_angle = Max_turn_angle + curvature
            else:
                #Car Offseted right--> Turn full wheels left
                CarTurn_angle = Max_turn_angle_neg + curvature
        else:
            # Within allowed distance limits for car and lane
            # Interpolate distance to Angle Range
            Turn_angle_interpolated = interp(distance,[-Max_Sane_dist,Max_Sane_dist],[Max_turn_angle_neg,Max_turn_angle])
            #[NEW]: Modified to calculate carturn_angle based on following criteria
            #             65% turn suggested by distance to the lane center + 35 % how much the lane is turning
            CarTurn_angle = (0.80*Turn_angle_interpolated) + (0.37*curvature)
            #print("+++++++++++++++Distance+++++++++++++++++:", Turn_angle_interpolated*0.8)
            #print("-----------------Curvature-----------------:",curvature*0.37)

        # Handle Max Limit [if (greater then either limits) --> set to max limit]
        if( (CarTurn_angle > Max_turn_angle) or (CarTurn_angle < (-1 *Max_turn_angle) ) ):
            if(CarTurn_angle > Max_turn_angle):
                CarTurn_angle = Max_turn_angle
            else:
                CarTurn_angle = -Max_turn_angle

        #angle = CarTurn_angle
        # [NEW]: Increase car turning capability by 30 % to accomodate sharper turns
        # angle = interp(CarTurn_angle,[-90,90],[-60,60])
        angle = CarTurn_angle

        curr_speed = car_speed
        
        # if (IncreaseTireSpeedInTurns and (Tracked_class !="left_turn")):
        

        
        return angle , curr_speed


def drive_car(Current_State):
        """Act on extracted information based on the SDC control mechanism

        Args:
            Current_State (List): information extracted from SDC surroundings 
                                    E.g. (Information regarding the lane boundaries for lane assist + 
                                        Information regarding the traffic signs for cruise control)
            Inc_TL (bool): Toggle [Intersection Navigation] ON | OFF 
            Inc_LT (bool): Toggle [Obey Left Turn Sign] ON | OFF 
        Returns:
            angle_of_car  (int): required steering angle for the SDC
            current_speed  (int): required cruise speed for the SDC 
            Detected_LeftTurn  (bool): Indicates if SDC has detected a left turn sign
            Activat_LeftTurn  (bool): Indicates if SDC Take_Left_Turn mechanism is activated
        """    

        # [NEW]: Deque member variable created for emulating rolling average filter to get smoothed Lane's ASsist 
        angle_queue = deque(maxlen=10)

        [Distance, Curvature, frame_disp] = Current_State

        current_speed = 0
        angle_of_car = 0
        
        if((Distance != -1000) and (Curvature != -1000)):

            # [NEW]: Very Important: Minimum Sane Distance that a car can be from the perfect lane to follow is increased to half its fov.
            #                        This means sharp turns only in case where we are way of target XD
            angle_of_car , current_speed = follow_Lane(int(frame_disp.shape[1]/2), Distance,Curvature)
        # [NEW]: Keeping track of orig steering angle and smoothed steering angle using rolling average
        config.angle_orig = angle_of_car
        # Rolling average applied to get smoother steering angles for robot
        angle_queue.append(angle_of_car)
        angle_of_car = (sum(angle_queue)/len(angle_queue))
        config.angle = angle_of_car

        return angle_of_car,current_speed

def display_state(frame_disp,angle_of_car,current_speed,Zebra_cross,Intersection_status):
        begin_row = 30
        row_step = 30
        font_size = 1.0
        thickness = 2

        max_speed = 50
        ###################################################  Displaying CONTROL STATE ####################################
        angle_str = "Angle = " + str(int(angle_of_car)) + "deg"
        cv2.putText(frame_disp,str(angle_str),(20,begin_row),cv2.FONT_HERSHEY_DUPLEX,font_size,(255,0,255),thickness)

        speed_str = "Speed = " + str(int(current_speed))
        if current_speed > max_speed:
            speed_str_clr = (255,0,255)
        else:
            speed_str_clr = (0,255,255)
        cv2.putText(frame_disp,str(speed_str),(20,begin_row+row_step),cv2.FONT_HERSHEY_DUPLEX,font_size,speed_str_clr,thickness)


        Zebra_cross_str = "Zebra_cross = " + str(Zebra_cross)
        if Zebra_cross:
            zebra_str_clr = (0, 255, 0)
        else:
            zebra_str_clr = (255,0,255)
        cv2.putText(frame_disp,str(Zebra_cross_str),(20,begin_row+row_step*2),cv2.FONT_HERSHEY_DUPLEX,font_size,zebra_str_clr,thickness)


        Intersection_str = "Intersection = " + Intersection_status
        if (Intersection_status == "False"):
            Intersection_str_clr = (255,0,255)
        else:
            Intersection_str_clr = (0, 255, 0)
        cv2.putText(frame_disp,str(Intersection_str),(20,begin_row+row_step*3),cv2.FONT_HERSHEY_DUPLEX,font_size,Intersection_str_clr,thickness)

def Lane_Detect_process(frame):
    # frame = cv2.resize(frame, (640,480))
    # print("..........In Lane process...........")
    distance, Curvature, Zebra_cross, Intersection_status = detect_Lane(frame)

    Current_State = [distance, Curvature, frame]
    Angle,Speed = drive_car(Current_State)
    
    result = frame.copy()
    print(f"1_Angle before ajustment : {Angle}")
    # Cong bu cho thuat toan (da chinh co khi cho di thang)
    if abs(Angle) < 7:
        Angle += 6.75 

    elif Angle >= 7:
        Angle += 12 -0.5

    elif Angle <= -13:
        Angle += 3.5+0.7
    elif -13 < Angle < -7:
        Angle += 7

    # Upper limit 
    if Angle > 25:
        Angle = 25
    elif Angle < -20:
        Angle = -20
    
    print(f"2_Angle after ajustment : {Angle}")

    if Zebra_cross:
        Speed = Speed*0.7

    if abs(Angle)>12.5:
            Speed *= 0.9
    if config.Testing:
        display_state(result,Angle,Speed,Zebra_cross, Intersection_status)

    # ~ cv2.imshow("Result",result)

    # ~ if cv2.waitKey(6) & 0xFF == ord('p'):   
        # ~ while True:
                # ~ if cv2.waitKey(10) & 0xFF == ord('p'):
                    # ~ break
    return Angle,Speed, result

if __name__ == "__main__":
    import cv2

    vidcap = cv2.VideoCapture("Records/night/bfmc2020_online_2.avi")
    success, image = vidcap.read()

    while success:
        success, image = vidcap.read()
        frame = image
        frame = cv2.resize(frame, (640,480))

        result = frame

        Lane_Detect_process(frame)

        if cv2.waitKey(6) & 0xFF == 27:   #ESC
                break
        
    vidcap.release()
    cv2.destroyAllWindows()
