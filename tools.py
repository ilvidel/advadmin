import subprocess as sp

import logger


def get_logger():
    return logger.Logger()


def execute(command):
    log = get_logger()

    child = sp.Popen(
        command,
        shell=True,
        stdout=sp.PIPE, stderr=sp.PIPE
    )

    out, err = child.communicate()
    if child.returncode != 0:
        log.fatal(err)

    if "error" in out:
        log.error(out)
        return None

    log.debug(out)
    return out
