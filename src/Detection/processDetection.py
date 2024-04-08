if __name__ == "__main__":
    import sys
    sys.path.insert(0, "../../..")

from src.templates.workerprocess import WorkerProcess
from src.Detection.threads.threadLane import threadLane
from src.Detection.threads.threadCameraDecision import threadCameraDecision


#---------------------------------------INIT-------------------------------------------#

class processDetection(WorkerProcess):
    def __init__(self, queueList, logging, debugging=False):
        self.queueList = queueList
        self.logger = logging
        self.debugging = debugging
        super(processDetection, self).__init__(self.queueList)
#--------------------------STOP----------------------------#
    def stop(self):
        """Function for stopping threads and the process."""
        for thread in self.threads:
            thread.stop()
            thread.join()
        super(processDetection, self).stop()

    # ===================================== RUN ==========================================
    def run(self):
        
        """Apply the initializing methods and start the threads."""
        super(processDetection, self).run()
    # ===================================== INIT TH =================================
    def _init_threads(self):
        """Initializes the threads."""
        LaneTh = threadLane(self.queuesList, self.logger, self.debugging)
        self.threads.append(LaneTh)
        CameraDecisionTh = threadCameraDecision(self.queuesList, self.logger, self.debugging)
        self.threads.append(CameraDecisionTh)
        print("Starting init thread detection\n")
    
