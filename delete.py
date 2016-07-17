#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import config
import json
import tools
from logger import Logger

CREDS = config.get_creds()
SERVER = config.get_server()
DBNAME = config.get_dbname()
FORCE_YES = False
log = tools.get_logger()


def delete(gameid):
    game = tools.get_game(gameid)
    if game is None:
        return

    cmd = 'curl -s --user {} -X DELETE {}/{}/{}?rev={}'.format(
        CREDS, SERVER, DBNAME, gameid, game['_rev']
    )

    if not FORCE_YES:
        log.warn("Borrando partido " + json.dumps(game, indent=2, sort_keys=True))
        check = raw_input('¿Seguro que quieres borrar el partido? (s/[n]): ')
        if not (check in ['s', 'S', 'y', 'Y']):
            log.info("Abortando...")
            sys.exit(1)

    out = tools.execute(cmd)
    if '"ok":true' in out:
        log.info("Partido borrado")
    else:
        log.error("Se ha producido un error")
        log.error(out)


if __name__ == "__main__":
    id_list = sys.argv[1:]

    if '-v' in id_list:
        log.level = Logger.Level.DEBUG
        id_list.remove('-v')

    if '-y' in id_list:
        FORCE_YES = True
        id_list.remove('-y')

    for i in id_list:
        delete(i)
