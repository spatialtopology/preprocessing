__all__ = [ 'preprocess', 'initialize']
# https://stackoverflow.com/questions/1944569/how-do-i-write-good-correct-package-init-py-files
# import utils._binarize_channel
# import utils._identify_boundary
# import utils._extract_runs
import logging
import os

def get_logger(name=None):
    """Return a logger to use"""
    return logging.getLogger("physio" + (".%s" % name if name else ""))

def set_logger_level(logger, level):
    if isinstance(level, int):
        pass
    elif level.isnumeric():
        level = int(level)
    elif level.isalpha():
        level = getattr(logging, level)
    else:
        logger.warning("Do not know how to treat loglevel %s" % level)
        return
    logger.setLevel(level)


# logger = get_logger()
# set_logger_level(logger, os.environ.get("SPACETOP_PHYSIO_LOG_LEVEL", logging.INFO))
