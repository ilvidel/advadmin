#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import datetime
import sys

import config
import game
import tools
from logger import Logger

FORCE_YES = False
NOT_REALLY = False
DB_NAME = config.get_dbname()
SERVER_URL = config.get_server()
CLOUDANT_CREDS = config.get_creds()
options = None
log = tools.get_logger()


def upload_game(game):
    """
    Upload one game to the database in the cloud
    """
    log.warn("Subiendo partido...")
    log.warn(str(game))

    if not FORCE_YES:
        check = raw_input("¿Es correcto? (s/[n]): ")
        if not (check in ['s', 'S', 'y', 'Y']):
            log.info("Abortando...")
            sys.exit(1)

    cmd = (
        "curl -s --user {0} {1}/{2} -X POST "
        "-H 'Content-Type: application/json' -d '{3}'"
        .format(CLOUDANT_CREDS, SERVER_URL, DB_NAME, str(game))
    )

    if NOT_REALLY:
        log.debug("Abortando subida por el uso del flag -n")
        return
    print("Before exec")
    out = tools.execute(cmd)
    print("After exec")
    log.debug(out)
    log.info("Subida correcta")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('local', help='Nombre del equipo local (entre comillas)')
    parser.add_argument('visitante', help='Nombre del equipo visitante (entre comillas)')
    parser.add_argument('categoria', choices=game.CATEGORY)
    parser.add_argument('division', choices=game.DIVISION)
    parser.add_argument('hora', help='Hora de comienzo del encuentro, en formato 24h (ej: 17:30')
    parser.add_argument('--fecha', help='Fecha del encuentro (se toma la actual por defecto. Formato: 27-3-16')
    parser.add_argument('-g', '--grupo', help='Grupo de competición (una letra)', default='-')
    parser.add_argument('--fase', help='Fase de la competición (por defecto, LIGA)', choices=game.PHASE, default='LIGA')
    parser.add_argument('--puntos-local', help='Puntos del equipo local, separados por comas (--puntos-local 25,19,25,25)', default=[])
    parser.add_argument('--puntos-visit', help='Puntos del equipo visitante, separados por comas (--puntos-local 23,25,20,21)', default=[])
    parser.add_argument('--notif', action='store_true', help='Enviar una notificación a los usuarios de la app', default=False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-n', '--not-really',
                       help='No hacer nada, solo indicarlo (para pruebas)',
                       action='store_true')
    group.add_argument('-y', '--force-yes',
                       help='Saltarse las preguntas de confirmación',
                       action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mostrar mucha información', default=False)

    options = parser.parse_args()

    if options.force_yes:
        FORCE_YES = True

    if options.not_really:
        NOT_REALLY = True

    print(log.level)
    if options.verbose:
        log.level = Logger.Level.DEBUG
    print(log.level)

    # TODO: PARSE OPTIONS, CREATE GAME OBJECT AND UPLOAD
    game = game.Game()
    game.local = options.local
    game.visit = options.visitante
    game.category = options.categoria
    game.division = options.division
    game.time = options.hora
    game.pool = options.grupo
    game.phase = options.fase
    game.local_points = options.puntos_local
    game.visit_points = options.puntos_visit

    if options.fecha is None:
        today = datetime.datetime.today()
        game.date = "{:02}-{:02}-{:04}".format(today.day, today.month, today.year)
    else:
        date = game.GameParser.checkDate(options.fecha)
        if date is None:
            sys.exit()
        game.set_date = date

    upload_game(game)
