"""
WHAT: A base class which will:
    * Define overridden method to find and set the executed file path
    * Define overridden method to set the parameters to be executed
    * Turns series of commands into a list
    * Executes the commands on the operating system
WHY: Bert python files do not allow for importing, you must shell them
ASSUMES: This is not meant to be used directly, this is mean to be used as base class
FUTURE IMPROVEMENTS: Convert to a "mixin" datatype, since its not meant to be instantiated by itself
WHO: SL 2020-08-28
"""

from abc import ABC, abstractmethod
from subprocess import Popen, PIPE, STDOUT
import sys
import logging
import modUtils


class clsBaseTask(ABC):
    """
    See header
    """

    def __init__(self):
        """
        Constructor
        """

        self.filePath = None  # the path to the python file being executed
        self.parameters = None  # command line parameters being passed to the file as a dictionary
        self.commands = None  # the executable + filePath + parameters, as a list

    @abstractmethod
    def __str__(self):
        """
        String method
        :return: None
        """
        pass

    @staticmethod
    def deleteFlags(FLAGS):
        """
        Reset the state of tensorflow, if you don't have this, the second file executed will crash
        :param FLAGS: Tensorflow flags
        :return: None
        """
        keys_list = [keys for keys in FLAGS._flags()]
        for keys in keys_list:
            FLAGS.__delattr__(keys)

    @abstractmethod
    def healthCheck(self):
        """
        Overriden method to determine if all files exist required to run the task
        :return: None
        """
        pass

    @abstractmethod
    def setFilePath(self):
        """
        Overridden method to find and set the filePath to be executed
        :return: None
        """
        pass

    @abstractmethod
    def setParameters(self):
        """
        Overridden method to set the parameters to be executed
        :return: None
        """
        pass

    def setCommands(self):
        """
        Combine the executable, filePath, and parameters as a list
        :return: None
        """
        self.commands = [sys.executable, self.filePath]
        for key, value in self.parameters.items():
            self.commands.append("--%s=%s" % (key, str(value)))

    def shellProcess(self):
        """
        Invoke the subprocess command to run the process on the operating system
        :return: None
        """
        modUtils.printAndLog("Shelling process: %s" % "\n" + " \\\n\t".join(self.commands))
        with Popen(self.commands, stdout=PIPE, stderr=STDOUT, bufsize=1) as process:
            for line in process.stdout:  # b'\n'-separated lines
                sys.stdout.buffer.write(line)  # pass bytes as is
                logging.debug(line)
        if process.returncode != 0:
            raise RuntimeError("%s command failed with exit code %s" % (str(self), str(process.returncode)))

    def execute(self):
        """
        Run all methods as a group
        :return: None
        """
        self.healthCheck()
        self.setFilePath()
        self.setParameters()
        self.setCommands()
        self.shellProcess()
