#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import urllib

import game
import tools
from logger import Logger
from tools import CMD_TEMPLATE


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
    log.debug("search query: " + query)
    return urllib.quote_plus(query)


def run_query(query):

    cmd = CMD_TEMPLATE + '_design/gamesearch/_search/searchAll?q={}&limit=200{}'
    log.debug(cmd.format(query, ''))

    out = tools.execute(cmd.format(query, ''))
    if out is None:
        return None

    response = json.loads(out)
    total = response['total_rows']
    bookmark = response['bookmark']
    game_list = response['rows']

    if total == 0:
        return None

    while len(game_list) < total:
        out = tools.execute(cmd.format(query, '&bookmark=' + bookmark))
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


def show_game(gameid):
    game = tools.get_game(gameid)
    print(json.dumps(game, indent=4, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id', help='Mostrar el partido con este identificador')
    parser.add_argument('-c', '--competicion', help='En qué competición buscar')
    parser.add_argument('-d', '--fecha', help='Fecha del encuentro. Pueden utilizarse comodines, por ejemplo: *-08-2016 para encontrar los partidos jugados en Agosto de 2016')
    parser.add_argument('-H', '--hora', help='Hora del encuentro')
    parser.add_argument('-e', '--equipo', help='Buscar un equipo')
    parser.add_argument('-C', '--categoria', help='Buscar partidos de esta categoría')
    parser.add_argument('-D', '--division', help='Buscar partidos de esta división')
    parser.add_argument('-f', '--fase', help='Fase de la competición (por defecto, LIGA)')
    parser.add_argument('-g', '--grupo', help='Buscar partidos de un grupo específico')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mostrar más información', default=False)

    options = parser.parse_args()
    if options.verbose:
        log.level = Logger.Level.DEBUG

    if not any(vars(options).values()):
        print(parser.print_help())
        log.error('Especifica al menos un criterio de búsqueda')
        exit(1)

    if options.id:
        show_game(options.id)
        exit(0)

    query = compose_query()
    result = run_query(query)
    show_result(result)
