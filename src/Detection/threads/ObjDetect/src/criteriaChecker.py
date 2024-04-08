from src.Detection.threads.ObjDetect.src.ratioAndAreaStandard import RATIO_TL_TOP, RATIO_TL_BOT, \
                RATIO_TS_TOP, RATIO_TS_BOT, \
                RATIO_HS_TOP, RATIO_HS_BOT, \
                RATIO_PE_TOP, RATIO_PE_BOT, \
                RATIO_CA_TOP, RATIO_CA_BOT, \
                AREA_TL_TOP, AREA_TL_BOT, \
                AREA_TS_TOP, AREA_TS_BOT, \
                AREA_HS_TOP, AREA_HS_BOT, \
                AREA_PE_TOP, AREA_PE_BOT, \
                AREA_CA_TOP, AREA_CA_BOT
class CriteriaChecker():
    def __init__(self):
       self.ratioStandard = {
           'trafficlight': { 'top': RATIO_TL_TOP, 'bottom': RATIO_TL_BOT},
           'trafficsign': { 'top': RATIO_TS_TOP, 'bottom': RATIO_TS_BOT},
           'highwaysign': { 'top': RATIO_HS_TOP, 'bottom': RATIO_HS_BOT},
           'person': { 'top': RATIO_PE_TOP, 'bottom': RATIO_PE_BOT},
           'car': { 'top': RATIO_CA_TOP, 'bottom': RATIO_CA_BOT},
        }

       self.areaStandard = {
           'trafficlight': { 'top': AREA_TL_TOP, 'bottom': AREA_TL_BOT},
           'trafficsign': { 'top': AREA_TS_TOP, 'bottom': AREA_TS_BOT},
           'highwaysign': { 'top': AREA_HS_TOP, 'bottom': AREA_HS_BOT},
           'person': { 'top': AREA_PE_TOP, 'bottom': AREA_PE_BOT},
           'car': { 'top': AREA_CA_TOP, 'bottom': AREA_CA_BOT},
        }

    def calculate(self, box):
        w = box[2] - box[0]
        h = box[3] - box[1]
        return w*h, h/w

    def process(self, box, className):
        area, ratio = self.calculate(box)
        # return True
        area_check = (self.areaStandard[className]['top'] >= area >= self.areaStandard[className]['bottom'])
        ratio_check = (self.ratioStandard[className]['top'] >= ratio >= self.ratioStandard[className]['bottom'])
        return area_check and ratio_check

        


