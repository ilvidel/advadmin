#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import datetime
import json
import os
import sys

import tools
from game import game
from logger import Logger

log = tools.get_logger()


def single_upload(game, not_really=False, force_yes=False):
    """
    Upload a single game to the database
    """
    if not os.path.exists(tools.TEMP_FILE):
        # create the empty game, if it doesn't exist
        with open(tools.TEMP_FILE, 'w+') as f:
            f.write(json.dumps(game, indent=2, sort_keys=True))

    # open the editor
    tools.edit_game()

    if not_really:
        log.debug("No se hace nada por usar el flag -n")
        sys.exit()

    if not force_yes:
        log.warn('')
        check = raw_input("¿Seguro que quieres subir el partido? (s/[n]): ")
        if not (check in ['s', 'S', 'y', 'Y']):
            log.info("Abortando...")
            sys.exit(1)

    # actually upload the game
    tools.upload_game()


def bulk_upload(game, not_really=False, force_yes=False):
    HEADER = (
        "# Escribe los datos de los partidos a subir. Cada partido en una linea, los campos separados por comas\n"
        "# y en el orden que se indica a continuacion:\n"
        "# FECHA HORA NOMBRE_COMPETICION DIVISION CATEGORIA FASE GRUPO LOCAL VISITANTE\n"
        "# Ejemplo:\n"
        "# 20-04-2016,13:00,liga regular 15-16,CADETE,MASCULINA,LIGA,-,Ayto. Miguelturra,CV La Roda\n"
    )

    if not os.path.exists(tools.TEMP_BULK_FILE):
        with open(tools.TEMP_BULK_FILE, "w") as f:
            f.write(HEADER)

    tools.edit_game(tools.TEMP_BULK_FILE)
    tools.bulk_upload()


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
    parser.add_argument('-m', '--muchos', action='store_true', help='Subir varios partidos a la vez', default=False)

    options = parser.parse_args()

    if options.verbose:
        log.level = Logger.Level.DEBUG

    # set some default data
    now = datetime.datetime.now()
    game['date'] = "{:02}-{:02}-{:04}".format(now.day, now.month, now.year)
    game['time'] = "{:02}:{:02}".format(now.hour, now.minute)

    if options.muchos:
        bulk_upload(game)
    else:
        single_upload(game)
