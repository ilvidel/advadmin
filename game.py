# -*- coding: utf-8 -*-

import datetime
import json
import re

PHASE = [
    'LIGA',
    'PLAY-OFF',
    'OCTAVOS',
    'CUARTOS',
    'BRONCE',
    'SEMIFINAL',
    'FINAL'
]

CATEGORY = [
    'OTRO',
    'SENIOR',
    'PRO',
    'SUPERLIGA',
    'SUPERLIGA2',
    'PRIMERA',
    'SEGUNDA',
    'JUVENIL',
    'CADETE',
    'INFANTIL',
    'ALEVIN',
    'AFICIONADOS'
]

DIVISION = [
    'MASCULINA',
    'FEMENINA',
    'MIXTO'
]


game = {
    'date': '01-01-1970',
    'time': '0:00',
    'competition': '',
    'category': 'SEGUNDA',
    'division': 'MASCULINA',
    'phase': 'LIGA',
    'pool': '-',
    'team1': {
        "name": "",
        "set1": "",
        "set2": "",
        "set3": "",
        "set4": "",
        "set5": ""
    },
    'team2': {
        "name": "",
        "set1": "",
        "set2": "",
        "set3": "",
        "set4": "",
        "set5": ""
    },
    'hall': '',
    'city': ''
}


class GameParser:

    def checkDate(date):
        valid = re.compile(r"^[0-9]{2}[/-][0-9]{2}[/-][0-9]{4}$")
        if valid.match(date) is None:
            raise ValueError(date + ' no es un formato de fecha correcto (DD-MM-AAAA)')

        tokens = re.findall(r"[\d]+", date)
        day = int(tokens[0])
        month = int(tokens[1])
        year = int(tokens[2])
        try:
            mydate = datetime.date(year, month, day)
        except:
            raise ValueError('La fecha introducida (%s) no es correcta' % date)

        if mydate < datetime.date.today():
            check = raw_input('La fecha %s está en el pasado. '
                          '¿Continuar de todos modos? (s/[n]): ' % date)
            if check not in ['s', 'y', 'S', 'Y']:
                print("Abortando...")
                return

        return "%02d-%02d-%04d" % (day, month, year)

    def checkTime(time):
        valid = re.compile(r"^[012]?[0-9]:[0-5][0-9]$")
        if valid.match(time) is None:
            raise ValueError(time + ' no se reconoce como una hora correcta (hh:mm)')

        tokens = time.split(':')
        if int(tokens[0]) > 24 or int(tokens[1]) > 59:
            raise ValueError('La hora introducida (%s) no es correcta' % time)

        return time

    def checkCategory(category):
        category = category.upper()
        if category not in CATEGORY:
            raise ValueError("Categoría no válida: '%s'" % category)
        return category

    def checkDivision(division):
        division = division.upper()
        if division not in DIVISION:
            raise ValueError("División no válida: '%s'" % division)
        return division

    def checkPool(pool):
        if len(pool) > 1:
            raise ValueError("Grupo no válido: '%s'" % pool)

        if pool == '-' or pool.isalnum():
            return pool
        else:
            raise ValueError("Grupo no válido '%s'" % pool)

    def checkPhase(phase):
        phase = phase.upper()
        if phase not in PHASE:
            raise ValueError("Fase no válida: '%s'" % phase)
        return phase

    def parseGame(line):
        """
        date time competition category division phase pool local visitor hall city
        """
        data = line.split(",")

        if len(data) < 11:
            raise ValueError("Faltan datos para el partido: " + line)

        date = GameParser.checkDate(data[0].strip())
        time = GameParser.checkTime(data[1].strip())
        comp = data[2].strip()
        cat = GameParser.checkCategory(data[3].strip())
        div = GameParser.checkDivision(data[4].strip())
        phase = GameParser.checkPhase(data[5].strip())
        pool = GameParser.checkPool(data[6].strip())
        local = data[7].strip()
        visit = data[8].strip()
        hall = data[9].strip()
        city = data[10].strip()

        return Game(date, time, comp, cat, div, phase, pool, local, visit, hall, city)
