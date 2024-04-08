class LightColor():
    def __init__(self):
        self.pickColor = ''
        self.haveMaxLen = False

        self.lightColorBuffer = {
            'redCount': {'count': 0},
            'greenCount': {'count': 0},
            'yellowCount': {'count': 0},
            'nocolorCount': {'count': 0}
        }
        
        self.color2count = {
            'red': 'redCount',
            'green': 'greenCount',
            'yellow': 'yellowCount',
            'nocolor': 'nocolorCount'
        }
        
        self.count2color = {
            'redCount': 'red',
            'greenCount': 'green',
            'yellowCount': 'yellow',
            'nocolorCount': 'none'
        }
    def reset_count(self):
        # Reset tất cả các count về 0
        for count in self.lightColorBuffer.values():
            count['count'] = 0
        self.haveMaxLen = False
        self.pickColor = 'none'

    def process(self, lightColor, maxLen=2):
        if self.haveMaxLen:
            self.reset_count()
        self.lightColorBuffer[self.color2count[lightColor]]['count'] += 1

        max_count = max(self.lightColorBuffer.values(), key=lambda x: x['count'])['count']
            
        for color, count in self.lightColorBuffer.items():
            if count['count'] >= maxLen:
                self.haveMaxLen = True
                self.pickColor = self.count2color[color]                      
            if count['count'] == max_count:
                self.pickColor = self.count2color[color]

        return self.pickColor, self.haveMaxLen
