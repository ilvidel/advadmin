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

CMD_TEMPLATE = 'curl -s --user {}:{} "http://{}.cloudant.com/{}/'.format(
    cfg.get('adv', 'user'),
    cfg.get('adv', 'passwd'),
    cfg.get('adv', 'server'),
    cfg.get('adv', 'dbname')
)


def get_logger():
    return log


def execute(command):
    log.debug("[ EXECUTE ] " + command)
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

    #log.debug(out)
    return out


def run_query(query):
    """
    Run a query on the database
    """
    cmd = CMD_TEMPLATE + '_design/gamesearch/_search/searchAll?q={}&limit=200{}"'
    out = execute(cmd.format(query, ''))
    if out is None:
        return None

    response = json.loads(out)
    total = response['total_rows']
    bookmark = response['bookmark']
    game_list = response['rows']

    if total == 0:
        return None

    while len(game_list) < total:
        out = execute(cmd.format(query, '&bookmark=' + bookmark))
        response = json.loads(out)
        game_list += response['rows']
        log.debug("found " + str(len(game_list)) + " games")
        bookmark = response['bookmark']
    return game_list


def get_game(gameid):
    """
    Retrieve a game from the database
    """
    cmd = CMD_TEMPLATE + gameid + '"'
    log.debug(cmd)
    out = execute(cmd)
    if out is None:
        get_logger().error("No se encuentra el partido " + gameid)
        return None

    game = json.loads(out)
    return game


def check_game():
    with open(TEMP_FILE, 'r') as f:
        game = json.loads(f.read())

    keys = ['competition', 'date', 'time', 'phase', 'category', 'division',
            'team1', 'team2', 'pool']

    for k in ['_id', '_rev']:   # we don't nee to compare these
        if k in game.keys():
            game.pop(k)

    try:
        assert sorted(game.keys()) == sorted(keys)
    except AssertionError:
        log.error("Falta algún campo en el documento")
        exit(1)

    healthy = True
    for i in keys:
        if game[i] == '':
            log.error("Debes especificar un valor para el campo '{}'".format(i))
            healthy = False
    if game['team1']['name'] == '':
        log.error("Debes especificar un nombre para el equipo 1")
        healthy = False
    if game['team2']['name'] == '':
        log.error("Debes especificar un nombre para el equipo 2")
        healthy = False

    if not healthy:
        exit(1)


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

    log.debug(cmd)
    sp.call(cmd.split())
    # check_game()


def get_next_id(competition):
    query = 'competition:\\"{}\\"'.format(urllib.quote(competition))

    all_games = run_query(query)
    if all_games is None:
        get_logger().fatal("Se ha producido un error:")
        exit(1)

    all_ids = [x['id'] for x in all_games]
    log.debug("len(all_ids): " + str(len(all_ids)))
    comp = competition.upper().replace(" ", "") + "_"
    i = 1
    while (comp + str(i) in all_ids):
        i += 1
    log.info("ID del partido: " + comp + str(i))
    return comp + str(i)


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
        log.debug("generando ID para el partido")
        competition = game['competition']
        gid = get_next_id(competition)
        competition = re.sub(" ", "", competition.upper())
        game['_id'] = gid

    cmd = (
        CMD_TEMPLATE + '"' + " -X POST -H 'Content-Type: application/json' -d '{}'"
        .format(json.dumps(game, sort_keys=True))
    )

    out = execute(cmd)
    if out is None:
        log.error("No se pudo actualizar el partido")
        return
    log.info(out)
    log.info("Subida correcta")
