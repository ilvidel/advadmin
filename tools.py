# -*- encoding: utf-8 -*-
import os
import re
import subprocess as sp
import urllib

import config
import json
import logger

DB_NAME = config.get_dbname()
SERVER_URL = config.get_server()
CLOUDANT_CREDS = config.get_creds()
TEMP_FILE = os.path.join('/tmp', 'game.json')
log = logger.Logger()


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
        'curl -s -u {} {}/{}/_design/gamesearch/_search/searchAll?q=competition:{}'
        .format(CLOUDANT_CREDS, SERVER_URL, DB_NAME, urllib.quote_plus(competition))
    )
    response = execute(cmd)
    if response is None or 'total_rows' not in response:
        get_logger().fatal("Se ha producido un error:")
        get_logger().info(response)
        exit(1)

    count = json.loads(response).get('total_rows', 0)
    return count + 1


def upload_game():
    """
    Upload the game stored in the temp file
    """
    f = open(TEMP_FILE, 'r')
    game = json.loads(''.join(f.readlines()))
    f.close()

    log.info("Subiendo partido...")

    if '_id' not in game:
        # need to create an ID
        competition = game['competition']
        gid = get_next_id(competition)
        competition = re.sub(" ", "", competition.upper())
        game['_id'] = "{}_{}".format(competition, gid)

    cmd = (
        "curl -s --user {0} {1}/{2} -X POST "
        "-H 'Content-Type: application/json' -d '{3}'"
        .format(CLOUDANT_CREDS, SERVER_URL, DB_NAME, json.dumps(game, sort_keys=True))
    )

    out = execute(cmd)
    if out is None:
        log.error("No se pudo actualizar el partido")
        return
    log.debug(out)
    log.info("Subida correcta")
