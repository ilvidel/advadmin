#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import datetime
import json
import sys

import tools
from game import game
from logger import Logger

log = tools.get_logger()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-n', '--not-really',
                       help='No hacer nada, solo indicarlo (para pruebas)',
                       action='store_true')
    group.add_argument('-y', '--force-yes',
                       help='Saltarse las preguntas de confirmación',
                       action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mostrar mucha información', default=False)
    options = parser.parse_args()

    if options.verbose:
        log.level = Logger.Level.DEBUG

    # set some default data
    now = datetime.datetime.now()
    game['date'] = "{:02}-{:02}-{:04}".format(now.day, now.month, now.year)
    game['time'] = "{:02}:{:02}".format(now.hour, now.minute)

    # write the game to a temprary file
    f = open(tools.TEMP_FILE, 'w+')
    f.write(json.dumps(game, indent=2, sort_keys=True))
    f.close()

    # open the editor
    tools.edit_game()

    if options.not_really:
        log.debug("No se hace nada por usar el flag -n")
        sys.exit()

    if not options.force_yes:
        log.warn('')
        check = raw_input("¿Seguro que quieres subir el partido? (s/[n]): ")
        if not (check in ['s', 'S', 'y', 'Y']):
            log.info("Abortando...")
            sys.exit(1)

    # actually upload the game
    tools.upload_game()
