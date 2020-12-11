"""
WHAT: A super class which will:
    * Define method to find and set the executed file path
    * Define method to set the parameters to be executed
WHY: Bert python files do not allow for importing, you must shell them
ASSUMES: This is a super class to clsBaseTask
FUTURE IMPROVEMENTS: N/A
WHO: SL 2020-08-28
"""

import modConfig
import modUtils
from tasks.clsBaseTask import clsBaseTask


class clsCreatePretrainingDataTask(clsBaseTask):
    """
    See header
    """

    def __init__(self, fileCounter):
        """
        Constructor, super-setting the base class
        """
        super().__init__()
        self.fileCounter = fileCounter

    def __str__(self):
        """
        Define string method
        :return: The string used for printing
        """
        return "create_pretraining_data.py"

    def healthCheck(self):
        """
        Method to determine if all files exist required to run the task
        :return: None
        """
        modUtils.printAndLog("Checking for input text file")
        if not modUtils.bucketFileExists(modConfig.inputTextFilePaths[self.fileCounter]):
            raise FileNotFoundError("Missing file %s" % modConfig.inputTextFilePaths[self.fileCounter])

        modUtils.printAndLog("Checking for bert vocab file")
        if not modUtils.bucketFileExists(modConfig.bertVocabFilePath):
            raise FileNotFoundError("Missing file %s" % modConfig.bertVocabFilePath)

    def setFilePath(self):
        """
        Imports the create_pretraining_data module and find its file path so it can be shelled.
        The module cannot be imported and used in that manner.
        :return: None
        """
        import tensorflow as tf
        import bert.create_pretraining_data
        self.filePath = bert.create_pretraining_data.__file__
        del bert
        self.deleteFlags(tf.flags.FLAGS)
        del tf

    def setParameters(self):
        """
        Set the parameters to be executed as a dictionary
        :return: None
        """
        self.parameters = {
            "input_file": modConfig.inputTextFilePaths[self.fileCounter],
            "output_file": modConfig.tensorflowRecordFilePaths[self.fileCounter],
            "vocab_file": modConfig.bertVocabFilePath,
            "do_lower_case": True,
            "max_seq_length": modConfig.max_seq_length,
            "max_predictions_per_seq": modConfig.max_predictions_per_seq,
            "masked_lm_prob": 0.15,
            "random_seed": 12345,
            "dupe_factor": 5,
        }
