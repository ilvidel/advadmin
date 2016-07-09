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
    'SUPERLIGA',
    'SUPERLIGA2',
    'PRIMERA',
    'SEGUNDA',
    'JUVENIL',
    'CADETE',
    'INFANTIL',
    'ALEVIN',
    'AFICIONADO'
]

DIVISION = [
    'MASCULINA',
    'FEMENINA',
    'MIXTO'
]


class Game:

    def __init__(self):
        self.__date = '01-01-1970'
        self.__time = '0:00'
        self.__competition = ''
        self.__category = 'SEGUNDA'
        self.__division = 'MASCULINA'
        self.__phase = 'LIGA'
        self.__pool = '-'
        self.__local = ''
        self.__local_points = []
        self.__visit_points = []
        self.__visit = ''
        self.__hall = ''
        self.__city = ''

    @property
    def date(self):
        return self.__date

    @property
    def time(self):
        return self.__time

    @property
    def competition(self):
        return self.__competition

    @property
    def category(self):
        return self.__category

    @property
    def division(self):
        return self.__division

    @property
    def phase(self):
        return self.__phase

    @property
    def pool(self):
        return self.__pool

    @property
    def local(self):
        return self.__local

    @property
    def visit(self):
        return self.__visit

    @property
    def hall(self):
        return self.__hall

    @property
    def city(self):
        return self.__city

    @property
    def local_points(self):
        return self.__local_points

    @property
    def visit_points(self):
        return self.__visit_points

    def toJson(self):
        dic = {}
        dic['date'] = self.date
        dic['time'] = self.time
        dic['competition'] = self.competition
        dic['category'] = self.category
        dic['division'] = self.division
        dic['phase'] = self.phase
        dic['pool'] = self.pool
        dic['local'] = self.local
        dic['local_points'] = self.local_points
        dic['visit'] = self.visit
        dic['visit_points'] = self.visit_points
        dic['hall'] = self.hall
        dic['city'] = self.city
        return dic

    def __str__(self):
        return json.dumps(self.toJson(), indent=3)

    @date.setter
    def date(self, d):
        self.__date = d

    @time.setter
    def time(self, time):
        self.__time = GameParser.checkTime(time)

    @competition.setter
    def competition(self, comp):
        self.__competition = comp.toupper()

    @category.setter
    def category(self, cat):
        self.__category = GameParser.checkCategory(cat)

    @division.setter
    def division(self, div):
        self.__division = GameParser.checkDivision(div)

    @phase.setter
    def phase(self, phase):
        self.__phase = GameParser.checkPhase(phase)

    @pool.setter
    def pool(self, pool):
        self.__pool = GameParser.checkPool(pool)

    @local.setter
    def local(self, local):
        self.__local = local.upper()

    @visit.setter
    def visit(self, visit):
        self.__visit = visit.upper()

    @local_points.setter
    def local_points(self, points):
        self.__local_points = points

    @visit_points.setter
    def visit_points(self, points):
        self.__visit_points = points

    @hall.setter
    def hall(self, hall):
        self.__hall = hall

    @city.setter
    def city(self, city):
        self.__city = city


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
            check = input('La fecha %s está en el pasado. '
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
