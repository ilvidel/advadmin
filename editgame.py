#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import os
import subprocess

import config
import tools
from logger import Logger


DB_NAME = config.get_dbname()
SERVER_URL = config.get_server()
CLOUDANT_CREDS = config.get_creds()
log = tools.get_logger()
options = None
TEMP_FILE = os.path.join('/tmp', 'game.json')


def get_game(gameid):
    game = tools.get_game(gameid)
    log.debug(json.dumps(game, indent=2))
    f = open(TEMP_FILE, 'w+')
    f.write(json.dumps(game, indent=2))
    f.close()


def edit_game():
    cmd = os.environ.get('EDITOR') + " " + TEMP_FILE
    log.debug(cmd)
    subprocess.call(cmd.split())


def upload_game():
    f = open(TEMP_FILE, 'r')
    game = json.loads(''.join(f.readlines()))
    f.close()

    cmd = (
        "curl -s --user {0} {1}/{2} -X POST "
        "-H 'Content-Type: application/json' -d '{3}'"
        .format(CLOUDANT_CREDS, SERVER_URL, DB_NAME, json.dumps(game))
    )

    out = tools.execute(cmd)
    if out is None:
        log.error("No se pudo actualizar el partido")
        return
    log.debug(out)
    log.info("Subida correcta")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('partido', help='Identificador del partido a editar. Usa findgame.py para averiguarlo')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mostrar más información', default=False)

    options = parser.parse_args()
    if options.verbose:
        log.level = Logger.Level.DEBUG

    get_game(options.partido)
    edit_game()
    upload_game()
