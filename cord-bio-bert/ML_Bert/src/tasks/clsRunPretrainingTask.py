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


class clsRunPretrainingTask(clsBaseTask):
    """
    See header
    """

    def __init__(self):
        """
        Constructor, super-setting the base class
        """
        super().__init__()

    def __str__(self):
        """
        Define string method
        :return: The string used for printing
        """
        return "run_pretraining.py"

    def healthCheck(self):
        """
        Method to determine if all files exist required to run the task
        :return: None
        """
        modUtils.printAndLog("Checking for tensorflow record files")
        for tensorflowRecordFilePath in modConfig.tensorflowRecordFilePaths:
            if not modUtils.bucketFileExists(tensorflowRecordFilePath):
                raise FileNotFoundError("Missing a file %s" % tensorflowRecordFilePath)

        modUtils.printAndLog("Checking for bert config file")
        if not modUtils.bucketFileExists(modConfig.bertConfigFilePath):
            raise FileNotFoundError("Missing file %s" % modConfig.bertConfigFilePath)

        modUtils.printAndLog("Checking for bert model checkpoint file")
        if not modUtils.bucketFileExists(modConfig.bertModelCheckpointFilePath + ".index"):
            raise FileNotFoundError("Missing file %s" % modConfig.bertModelCheckpointFilePath + ".index")

    def setFilePath(self):
        """
        Imports the run_pretraining module and find its file path so it can be shelled.
        The module cannot be imported and used in that manner.
        :return: None
        """
        import tensorflow as tf
        import bert.run_pretraining
        self.filePath = bert.run_pretraining.__file__
        del bert
        self.deleteFlags(tf.flags.FLAGS)
        del tf

    def setParameters(self):
        """
        Set the parameters to be executed as a dictionary
        :return: None
        """
        self.parameters = {
            "input_file": modConfig.tensorflowRecordFilePathPattern,
            "output_dir": modConfig.outputRunFolderPath,
            "do_train": True,
            "do_eval": True,
            "bert_config_file": modConfig.bertConfigFilePath,
            "init_checkpoint": modConfig.bertModelCheckpointFilePath,
            "train_batch_size": 192,
            "max_seq_length": modConfig.max_seq_length,
            "max_predictions_per_seq": modConfig.max_predictions_per_seq,
            "num_train_steps": 200000,
            "num_warmup_steps": 10,
            "save_checkpoints_steps": 50000,
            "learning_rate": "2e-5",
            "use_tpu": True,
            "tpu_name": modConfig.tpuName,
            "tpu_zone": modConfig.tpuZone,
        }
