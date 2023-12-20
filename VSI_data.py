class Frame:
    def __init__(self,time,image,name): 
        
        self.time = time
        self.images = {name: image}
        self.last_data = image
        self.save_image = image
        
    def getTime(self):
        return self.time
        
    def getImage(self,name):
        return self.images[name]   
        
    def getSaveImage(self):
        return self.save_image
        
    def getLastImage(self):
        return self.last_data
        
    def getImages(self):
        return self.images

    def addData(self,data,name):
        
        self.images[name] = data[0]
        self.last_data = data[1]