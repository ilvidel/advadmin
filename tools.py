import colorlog
import subprocess as sp


def get_logger(name):
    handler = colorlog.StreamHandler()
    fmt = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s:: %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'white',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    handler.setFormatter(fmt)
    logger = colorlog.getLogger(name)
    logger.addHandler(handler)
    return logger


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
