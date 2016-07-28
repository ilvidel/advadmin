# -*- coding: utf-8 -*-

import datetime
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
        "set1": 0,
        "set2": 0,
        "set3": 0,
        "set4": 0,
        "set5": 0
    },
    'team2': {
        "name": "",
        "set1": 0,
        "set2": 0,
        "set3": 0,
        "set4": 0,
        "set5": 0
    },
    'hall': '',
    'city': ''
}


class GameParser:

    def checkDate(self, date):
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

    def checkTime(self, time):
        valid = re.compile(r"^[012]?[0-9]:[0-5][0-9]$")
        if valid.match(time) is None:
            raise ValueError(time + ' no se reconoce como una hora correcta (hh:mm)')

        tokens = time.split(':')
        if int(tokens[0]) > 24 or int(tokens[1]) > 59:
            raise ValueError('La hora introducida (%s) no es correcta' % time)

        return time

    def checkCategory(self, category):
        category = category.upper()
        if category not in CATEGORY:
            raise ValueError("Categoría no válida: '%s'" % category)
        return category

    def checkDivision(self, division):
        division = division.upper()
        if division not in DIVISION:
            raise ValueError("División no válida: '%s'" % division)
        return division

    def checkPool(self, pool):
        if len(pool) > 1:
            raise ValueError("Grupo no válido: '%s'" % pool)

        if pool == '-' or pool.isalnum():
            return pool
        else:
            raise ValueError("Grupo no válido '%s'" % pool)

    def checkPhase(self, phase):
        phase = phase.upper()
        if phase not in PHASE:
            raise ValueError("Fase no válida: '%s'" % phase)
        return phase

    def parseGame(self, line):
        """
        date time competition category division phase pool local visitor (hall city)
        """
        fields = line.split(",")

        if len(fields) < 9:
            raise ValueError("Falta algún campo en la línea")

        game = {}
        game['date'] = self.checkDate(fields[0].strip())
        game['time'] = self.checkTime(fields[1].strip())
        game['comp'] = fields[2].strip()
        game['cat'] = self.checkCategory(fields[3].strip())
        game['div'] = self.checkDivision(fields[4].strip())
        game['phase'] = self.checkPhase(fields[5].strip())
        game['pool'] = self.checkPool(fields[6].strip())
        game['local'] = fields[7].strip()
        game['visit'] = fields[8].strip()
        # game['hall'] = fields[9].strip()
        # game['city'] = fields[10].strip()

        return game
