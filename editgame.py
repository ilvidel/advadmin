#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json

import config
import tools
from logger import Logger

DB_NAME = config.get_dbname()
SERVER_URL = config.get_server()
CLOUDANT_CREDS = config.get_creds()
log = tools.get_logger()
options = None


def get_game(gameid):
    game = tools.get_game(gameid)
    log.debug(json.dumps(game, indent=2, sort_keys=True))
    f = open(tools.TEMP_FILE, 'w+')
    f.write(json.dumps(game, indent=2, sort_keys=True))
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('partido', help='Identificador del partido a editar. Usa findgame.py para averiguarlo')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mostrar más información', default=False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-n', '--not-really', help='No hacer nada, solo indicarlo (para pruebas)', action='store_true')
    group.add_argument('-y', '--force-yes', help='Saltarse las preguntas de confirmación', action='store_true')

    options = parser.parse_args()
    if options.verbose:
        log.level = Logger.Level.DEBUG

    get_game(options.partido)

    # open the editor
    tools.edit_game()

    if options.not_really:
        log.debug("No se hace nada por usar el flag -n")
        exit()

    if not options.force_yes:
        log.warn('')
        check = raw_input("¿Seguro que quieres subir el partido? (s/[n]): ")
        if not (check in ['s', 'S', 'y', 'Y']):
            log.info("Abortando...")
            exit(1)

    # actually upload the game
    tools.upload_game()
