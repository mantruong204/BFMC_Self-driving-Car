import os
import sys
import imutils



from src.Detection.threads.ObjDetect.src.yoloDet import YoloTRT
from src.Detection.threads.ObjDetect.src.lightColor import LightColor
from src.Detection.threads.ObjDetect.src.TLClassify import TLClassification
from src.Detection.threads.ObjDetect.src.criteriaChecker import CriteriaChecker

class RunAIThread():
    def __init__(self):
        self.libraryPath = "src/Detection/threads/ObjDetect/models/trt/libmyplugins.so"
        # self.enginePath = "src/Detection/threads/ObjDetect/models/trt/bestn_full.engine"
        self.enginePath = "src/Detection/threads/ObjDetect/models/trt/bests_12class_tan.engine"
        
        self.model = YoloTRT(library=self.libraryPath, engine=self.enginePath, conf=0.5, yolo_ver="v5")
        # print("55555555555555555555555555Created YOLO TRT")
        self.light = LightColor()
        self.checker = CriteriaChecker()

        self.output = {
            'light_color': {'class': 'none', 'box': 'none', 'conf': 'none' },
            'sign_type': {'class': 'none', 'box': 'none', 'conf': 'none' },
            'object': {'class': 'none', 'box': 'none', 'conf': 'none' }
        }
    
    def process(self, frame):
        frame = imutils.resize(frame, width=640)
        detections, _ = self.model.Inference(frame)
        if not detections:
            self.output = {
            'light_color': {'class': 'none', 'box': 'none', 'conf': 'none' },
            'sign_type': {'class': 'none', 'box': 'none', 'conf': 'none' },
            'object': {'class': 'none', 'box': 'none', 'conf': 'none' }
        }
        else:
            for obj in detections:        
                box = obj['box'].astype(int)
                img = frame[box[1]:box[3], box[0]:box[2]]
                className = obj['class']

                if className == 'trafficlight':
                    reasonableSize = self.checker.process(box, className=className)
                    if reasonableSize:
                        colorClassification = TLClassification(img)
                        color, _ = self.light.process(colorClassification)
                    else:
                        color = 'none'
                    self.output['light_color'] = {'class': color, 'box': obj['box'], 'conf' : obj['conf']}


                elif className in ['person', 'car']:
                    reasonableSize = self.checker.process(box, className=className)
                    if reasonableSize:
                        self.output['object'] = {'class': obj['class'], 'box': obj['box'], 'conf' : obj['conf']}
                    else:
                        self.output['object'] = {'class': 'none', 'box': 'none', 'conf': 'none' }


                elif className in ["crosswalk", "roundAbout", "noentry", "oneway", "parking", "priority", "stop"]:
                    reasonableSize = self.checker.process(box, className='trafficsign')
                    if reasonableSize:
                        self.output['sign_type'] = {'class': obj['class'], 'box': obj['box'], 'conf' : obj['conf']}
                    else: 
                        self.output['sign_type'] = {'class': 'none', 'box': 'none', 'conf': 'none' }
                elif className in ["enterHighway", "endHighway"]:
                    reasonableSize = self.checker.process(box, className='highwaysign')
                    if reasonableSize:
                        self.output['sign_type'] = {'class': obj['class'], 'box': obj['box'], 'conf' : obj['conf']}
                    else: 
                        self.output['sign_type'] = {'class': 'none', 'box': 'none', 'conf': 'none' }
        return self.output
