class Record:
    def __init__(self,device_info,times,video_path):
        self.device = device_info
        self.times = times
        self.video_path = video_path
            
    def getInfo(self):
        return self.device
    
    def getTimes(self):
        return self.times
        
    def getVideoPath(self):
        return self.video_path
    

        
        