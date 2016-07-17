import subprocess as sp

import config
import json
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
        log.fatal(err or out)
        return None

    if "error" in out:
        log.error(out)
        return None

    log.debug(out)
    return out


def get_game(gameid):
    cmd = 'curl -s --user {} {}/{}/{}'.format(
        config.get_creds(),
        config.get_server(),
        config.get_dbname(),
        gameid
    )
    out = execute(cmd)
    if out is None:
        get_logger().error("No se encuentra el partido " + gameid)
        return None

    game = json.loads(out)
    return game
