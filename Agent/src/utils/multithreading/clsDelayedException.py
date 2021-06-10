import sys
# import tblib.pickling_support


class clsDelayedException(Exception):

    def __init__(self, ee):
        self.ee = ee
        __, __, self.tb = sys.exc_info()
        super(clsDelayedException, self).__init__(str(ee))

    def re_raise(self):
        raise self.ee.with_traceback(self.tb)


# install after all custom exceptions have been declared
# this is only required for multiprocessing
# since the dispatcher could be either MT or MP, we leave this alone
# tblib.pickling_support.install()
