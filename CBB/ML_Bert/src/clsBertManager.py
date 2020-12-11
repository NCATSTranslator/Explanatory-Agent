"""
WHAT: A class which will:
    * Run a list of tasks in sequence to the operating system
WHY: Need an object which manages the entire data flow in the program
ASSUMES: 1 instance only, no need for more instances, but there's no static class in python
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-28
"""

from tasks.clsCreatePretrainingDataTask import clsCreatePretrainingDataTask
from tasks.clsRunPretrainingTask import clsRunPretrainingTask
import modUtils
import modConfig


class clsBertManager:
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """
        self.createPretrainingDataTasks = []
        self.runPretrainingTask = None

    def createTasks(self):
        """
        Determine what tasks to run based on what files are available in the Google bucket
        :return: None
        """
        self.createPretrainingDataTasks = []
        for i, tensorflowRecordFilePath in enumerate(modConfig.tensorflowRecordFilePaths):
            if not modUtils.bucketFileExists(tensorflowRecordFilePath):
                self.createPretrainingDataTasks.append(clsCreatePretrainingDataTask(fileCounter=i))
                modUtils.printAndLog("Tensorflow record file path not found %s, adding %s" % (tensorflowRecordFilePath, str(self.createPretrainingDataTasks[-1])))
        self.runPretrainingTask = clsRunPretrainingTask()

    def runTasks(self):
        """
        Run tasks in sequence
        :return: None
        """
        modUtils.printAndLog("Running tasks")

        if self.createPretrainingDataTasks:
            for createPretrainingDataTask in self.createPretrainingDataTasks:
                modUtils.printAndLog("Executing %s" % str(createPretrainingDataTask))
                createPretrainingDataTask.execute()

        modUtils.printAndLog("Executing %s" % str(self.runPretrainingTask))
        self.runPretrainingTask.execute()

        modUtils.printAndLog("All tasks complete")

    def execute(self):
        """
        Run all methods as a group of functions
        :return: None
        """
        self.createTasks()
        self.runTasks()
