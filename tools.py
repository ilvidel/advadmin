import subprocess as sp

import logger


def get_logger(name):
    return logger.Logger()


def execute(command):
    log = get_logger('')

    child = sp.Popen(
        command,
        shell=True,
        stdout=sp.PIPE, stderr=sp.PIPE
    )

    out, err = child.communicate()
    if child.returncode != 0:
        log.error(err)

    log.debug(out)
    return out
