#!/usr/bin/python
# Recurring Transactions for Ledger (dklrt).
# (c) Kevin Keegan 2011-07-20.
# (c) David Keegan 2011-08-06.

import sys, os, re
import Time, Misc

class Transaction:
   _ReTxStart = re.compile('^(%s)(\s*)\((%s)\)' %\
    (Time.ReDate, Time.RePeriod))

   _ReComment = re.compile('^\s*;')
   _ReWhitespace = re.compile('^\s*$')

   def __init__(self, Parent, Line=None):
      self._Parent = Parent
      self._DateStr = None     # Date String.
      self._DateObject = None      # Date in datetime.date format
      self._Ds = None       # Actual Date Separator.
      self._Period = None   # Period String.
      self._Al = []         # Additional Lines (after date).
      if not Line is None: self._Set(Line)

   def __repr__(self):
      return Misc.Repr('Date=%r,Dis=%r,Ds=%r,Period=%r,Al=%r' %\
       (self._DateStr, self._DateObject, self._Ds, self._Period, self._Al), self)

   def __str__(self):
      """As a string, including the period."""
      return self._DateLine() + self._RemainderLines()

   def TransactionText(self):
      """As a string, excluding the period."""
      return self._DateLine(True) + self._RemainderLines(True)

   def _DateLine(self, ExcludePeriod=False):
      """The Date line."""
      Pt = '' if ExcludePeriod else '%s(%s)' % (self._Ds, self._Period)
      return '%s%s%s' % (self._DateStr, Pt, self._Al[0])

   def _RemainderLines(self, ExcludeEmpty=False):
      Rv = ''
      if ExcludeEmpty:
         for Rl in self._Al[1:]:
            if not re.match(self._ReWhitespace, Rl):
               Rv = Rv + Rl
      else:
         Rv = ''.join(self._Al[1:]) 
      return Rv

   def __nonzero__(self):
      return self._DateStr is not None

   def _Log(self, Msg): Misc.Log(Msg, self)
   def _Throw(self, Msg): Misc.Throw(Msg, self)

   def _Set(self, Line):
      self.__init__(self._Parent)
      Match = re.match(self._ReTxStart, Line)
      if Match:
         self._DateStr = Match.group(1)
         self._DateObject = Time.DateStrtoDatetime(self._DateStr)
         self._Ds = Match.group(2)
         self._Period = Match.group(3)
         Dlen = len(Match.group(0))
         self.Add(Line[Dlen:])

   def Add(self, Line):
      self._Al.append(Line)

   def Generate(self):
      """Generates transaction(s) for the current config entry.

         One transaction per interval up to to and including the
         target date. In normal operation zero or one transactions are
         generated, but if processing has been delayed, more than one
         transaction can be produced.
         
         Returns a list of transaction strings ready for sorting and
         output to a ledger file. Each one begins with a newline to
         ensure it is separated by an empty line on output.
      """
      Rv = []
      TargetDateObject = self._Parent._TargetDateObject
      Done = False
      while not Done:
         if self._DateObject > TargetDateObject: Done = True
         else:
            # Append transaction text.
            Rv.append('\n' + self.TransactionText())

            # Evaluate next posting date.
            NewDateObject = Time.DateAddPeriod(self._DateObject, self._Period)
            if NewDateObject <= self._DateObject:
               _Throw("Period is negative or zero!")
            self._DateObject = NewDateObject
            self._DateStr = Time.DateToText(self._DateObject)
      return Rv
       
class Transactions:
   def __init__\
   (self,
    LedgerFileName=None,
    TargetDatetimeObject=None,
    ConfigFileName=None):
      self._Lfn = LedgerFileName
      self._Cfn = ConfigFileName
      self._TargetDateObject = TargetDatetimeObject
      if self._TargetDateObject is None:
         self._TargetDateObject = Time.DateToday()
      self._Nrt = 0            # No of Recurring Transactions.
      self._Preamble = ''
      self._Rtl = []           # Recurring Transaction List.
      self._ReadConfig()

   def __repr__(self):
      return Misc.Repr('Lfn=%r,Cfn=%r,TargetDateObject=%r,Nrt=%r,Preamble=%r,Rtl=%r' %\
       (self._Lfn, self._Cfn, self._TargetDateObject, self._Nrt, self._Preamble,
        self._Rtl), self)

   def __str__(self):
      Rv = self._Preamble
      for Rt in self._Rtl:
         Rv = Rv + str(Rt)
      return Rv

   def _Log(self, Msg): Misc.Log(Msg, self)
   def _Throw(self, Msg): Misc.Throw(Msg, self)

   def _ReadConfig(self):
      Rt = None
      Af = open(self._Cfn)
      for Line in Af:
         RtNew = Transaction(self, Line)
         if RtNew:
            # Line is start of new transaction.
            self._Nrt = self._Nrt + 1
            if Rt is not None: self._Rtl.append(Rt)
            Rt = RtNew
         else:
            # Line does not start a transaction.
            if self._Nrt <= 0:
               # Append to preamble.
               self._Preamble = self._Preamble + Line
            else:
               # Line continues a transaction.
               Rt.Add(Line)
      if Rt is not None: self._Rtl.append(Rt)
      Af.close()

   def Generate(self):
      """Generates transactions up to and including the target date.
         Returns a list of strings ready for sorting and output to a
         ledger file.
      """
      Rv = []
      for Rt in self._Rtl:
         Rv.extend(Rt.Generate())
      return sorted(Rv)

   def Post(self):
      """Generates recurring transactions and posts to ledger file."""
      Posts = self.Generate()

      if len(Posts):
         # Best attempt to ensure either both writes succeed or none.
         Cf = open(self._Cfn, 'w')
         Lf = open(self._Lfn, 'a')
         Cf.write(self.__str__())
         Lf.writelines(Posts)
         Lf.close()
         Cf.close()

def main(Argv=None):
   if Argv is None: Argv = sys.argv
   Lfn = None if len(Argv) < 1 else Argv[0]
   TargetDateObject = None if len(Argv) < 2 else Time.DateStrtoDatetime(Argv[1])
   Cfn = None if len(Argv) < 3 else Argv[2]
   Rts = Transactions(Lfn, TargetDateObject, Cfn)
   Rts.Post()
   return 0

if __name__ == "__main__":
   sys.exit(main(sys.argv[1:]))
