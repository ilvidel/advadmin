#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import urllib

import config
import game
import tools
from logger import Logger

DB_NAME = config.get_dbname()
SERVER_URL = config.get_server()
CLOUDANT_CREDS = config.get_creds()
log = tools.get_logger()
options = None


def compose_query():
    criteria = []

    if options.competicion:
        criteria.append('competition:' + options.competicion)
    if options.fecha:
        criteria.append('date:' + options.fecha)
    if options.hora:
        criteria.append('time:"{}"'.format(options.hora))  # need quotes because of colon ':'

    if options.categoria:
        cat = options.categoria
        if cat.upper() not in game.CATEGORY:
            cat = options.categoria + '*'
            log.warn('Categoria "{}" desconocida, usando comodines: {}'.format(options.categoria, cat))
        criteria.append('category:' + cat)

    if options.division:
        div = options.division
        if div.upper() not in game.DIVISION:
            div = options.division + '*'
            log.warn('Division "{}" desconocida, usando comodines: {}'.format(options.division, div))
        criteria.append('division:' + div)

    if options.fase:
        fase = options.fase
        if fase.upper() not in game.PHASE:
            fase = options.fase + '*'
            log.warn('Fase "{}" desconocida, usando comodines: {}'.format(options.fase, fase))
        criteria.append('phase:' + fase)

    if options.grupo:
        criteria.append('group:' + options.grupo)
    if options.equipo:
        criteria.append('team1:{0} OR team2:{0}'.format(options.equipo))

    query = ' AND '.join(criteria)
    return urllib.quote_plus(query)


def run_query(query):
    cmd = 'curl -s --user {0} "{1}/{2}/_design/gamesearch/_search/searchAll?q={3}&limit=200{4}"'

    log.debug(cmd.format("", SERVER_URL, DB_NAME, query, ''))

    out = tools.execute(cmd.format(CLOUDANT_CREDS, SERVER_URL, DB_NAME, query, ''))
    if out is None:
        return None

    response = json.loads(out)
    total = response['total_rows']
    bookmark = response['bookmark']
    game_list = response['rows']

    if total == 0:
        return None

    while len(game_list) < total:
        out = tools.execute(cmd.format(
            CLOUDANT_CREDS, SERVER_URL, DB_NAME, query,
            '&bookmark=' + bookmark
        ))
        response = json.loads(out)
        game_list += response['rows']
        bookmark = response['bookmark']
    return game_list


def show_result(game_list):
    if game_list is None:
        log.info("No se han encontrado partidos con esos criterios")
        return

    log.info("Se han encontrado {} partidos".format(len(game_list)))
    print('\n')

    for g in game_list:
        fields = g['fields']
        print('ID: {0}\n{1}   {2}   {3} {4}   {5} vs {6}\n\n'.format(
            g['id'],
            fields.get('competition', ''),
            fields.get('date', ''),
            fields.get('category', ''),
            fields.get('division', ''),
            fields.get('team1', ''),
            fields.get('team2', '')
        ))
    log.info("Se han encontrado {} partidos".format(len(game_list)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--competicion', help='En qué competición buscar')
    parser.add_argument('--fecha', help='Fecha del encuentro. Pueden utilizarse comodines, por ejemplo: *-08-2016 para encontrar los partidos jugados en Agosto de 2016')
    parser.add_argument('--hora', help='Hora del encuentro')
    parser.add_argument('--equipo', help='Buscar un equipo')
    parser.add_argument('--categoria', help='Buscar partidos de esta categoría')
    parser.add_argument('--division', help='Buscar partidos de esta división')
    parser.add_argument('--fase', help='Fase de la competición (por defecto, LIGA)')
    parser.add_argument('--grupo', help='Buscar partidos de un grupo específico')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mostrar más información', default=False)

    options = parser.parse_args()
    if options.verbose:
        log.level = Logger.Level.DEBUG

    if not any(vars(options).values()):
        print(parser.print_help())
        log.error('Especifica al menos un criterio de búsqueda')
        exit(1)

    query = compose_query()
    result = run_query(query)
    show_result(result)
