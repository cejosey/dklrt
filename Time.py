#!/usr/bin/python
# Time and Date Utilities (dklrt).
# (c) David Keegan 2011-08-06.
import sys, re
import time
import datetime
import datetime
import Misc
from dateutil.relativedelta import relativedelta

ModuleName = __name__
ReDateSep = '[-/]'
ReDate = '\d{4}%s\d{1,2}%s\d{1,2}' % (ReDateSep, ReDateSep)
RePeriod = '(\d+)([ymwdh])'

DateFormat = '%Y/%m/%d'

ReDateTimeSep = "[-/: ]";
DateTimeFormat = '%Y%m%d%H%M%S'

SecPerHour = 60
SecPerDay = 24 * SecPerHour * SecPerHour

def _Throw(Msg): Misc.Throw(Msg, ModuleName)

def DateToText(DatetimeObject):
    return datetime.date.strftime(DatetimeObject, DateFormat)

def DateToday():
    return datetime.date.today()

def DateStrtoDatetime(DateString):
    year = int(DateString[0:4])
    month = int(DateString[5:7])
    day = int(DateString[8:10])
    return datetime.date(year, month, day)
    
def DateAddPeriod(DatetimeObject, Periodstr):
   """Adds the period to the Seconds (a date)."""
   Match = re.match(RePeriod, Periodstr)
   if not Match: _Throw("Bad Period String: %s!" % Periodstr)
   Count = int(Match.group(1))
   Unit = Match.group(2)

   if Unit == 'y': Rv = DatetimeObject + relativedelta(years = +Count)
   elif Unit== 'm': Rv = DatetimeObject + relativedelta(months = +Count)
   elif Unit == 'w': Rv = DatetimeObject + relativedelta(weeks = +Count)
   elif Unit == 'd': Rv = DatetimeObject + relativedelta(days = +Count)
   else: _Throw('Bad Period Unit: "%s"!' % Unit)
   return Rv
