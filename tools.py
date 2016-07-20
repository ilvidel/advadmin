# -*- encoding: utf-8 -*-
import configparser
import os
import re
import subprocess as sp
import urllib

import json
import logger


TEMP_FILE = os.path.join('/tmp', 'game.json')
log = logger.Logger()
cfg = configparser.ConfigParser()
cfg.read('config.ini')

CMD_TEMPLATE = 'curl -s --user {}:{} http://{}.cloudant.com/{}/'.format(
    cfg.get('adv', 'user'),
    cfg.get('adv', 'passwd'),
    cfg.get('adv', 'server'),
    cfg.get('adv', 'dbname')
)


def get_logger():
    return log


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
    """
    Retrieve a game from the database
    """
    cmd = CMD_TEMPLATE + gameid
    log.debug(cmd)
    out = execute(cmd)
    if out is None:
        get_logger().error("No se encuentra el partido " + gameid)
        return None

    game = json.loads(out)
    return game


def edit_game():
    """
    Edit a game using the default editor.
    """
    editor = os.environ.get('EDITOR')
    if editor is None:
        get_logger().fatal("No se encuentra ningún editor")
        get_logger().info("Por favor, define uno en la variable de entorno EDITOR")
        exit(1)

    cmd = editor + " " + TEMP_FILE

    get_logger().debug(cmd)
    sp.call(cmd.split())


def get_next_id(competition):
    cmd = (
        CMD_TEMPLATE + '_design/gamesearch/_search/searchAll?q=competition:{}'
        .format(urllib.quote_plus(competition))
    )
    response = execute(cmd)
    if response is None or 'total_rows' not in response:
        get_logger().fatal("Se ha producido un error:")
        get_logger().info(response)
        exit(1)

    count = json.loads(response).get('total_rows', 0)
    return count + 1


def remove_special_chars(text):
    if text is None:
        return ""

    replacements = {
        'á': 'a',
        'é': 'e',
        'í': 'i',
        'ó': 'o',
        'ú': 'u',
        'ñ': 'n',
        'ü': 'u',
        'Á': 'A',
        'É': 'E',
        'Í': 'I',
        'Ó': 'O',
        'Ú': 'U',
        'Ñ': 'N',
        'Ü': 'U',
    }
    regex = re.compile("(%s)" % "|".join(map(re.escape, replacements.keys())))
    return regex.sub(lambda x: str(replacements[x.string[x.start():x.end()]]), text)


def upload_game():
    """
    Upload the game stored in the temp file
    """
    text = None
    with open(TEMP_FILE, 'r') as f:
        text = ''.join(f.readlines())
    game = json.loads(remove_special_chars(text))

    log.info("Subiendo partido...")

    if '_id' not in game:
        # need to create an ID
        competition = game['competition']
        gid = get_next_id(competition)
        competition = re.sub(" ", "", competition.upper())
        game['_id'] = "{}_{}".format(competition, gid)

    cmd = (
        CMD_TEMPLATE + " -X POST -H 'Content-Type: application/json' -d '{}'"
        .format(json.dumps(game, sort_keys=True))
    )

    out = execute(cmd)
    if out is None:
        log.error("No se pudo actualizar el partido")
        return
    log.debug(out)
    log.info("Subida correcta")
