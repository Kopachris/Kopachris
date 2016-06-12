#!/usr/bin/env python3

import cmd
import sys
import sqlite3

from time import time


tbl_punches_in = """
CREATE TABLE IF NOT EXISTS punches_in (
    date REAL
)
"""

tbl_punches_out = """
CREATE TABLE IF NOT EXISTS punches_out (
    date REAL, time_worked INT
)
"""

tbl_withdrawls = """
CREATE TABLE IF NOT EXISTS withdrawls (
    date REAL, amount REAL
)
"""

tbl_balance = """
CREATE TABLE IF NOT EXISTS balance (
    date REAL, time_worked INT, amount REAL
)
"""


class PayrollShell(cmd.Cmd):
    intro = "Payroll database command line.\nType help or ? to list commands."
    prompt = "(local) ?? "
    
    def punch_in(self):
        self.cur.execute("INSERT INTO punches_in VALUES (?)", (time(),))
        self.db.commit()
        
    def punch_out(self, last_in):
        # get time worked in 15-min increments
        now = time()
        time_worked = round((now - last_in[0]) / 60 / 15)
        
        # get rounded hours worked for display
        hours_worked = time_worked * 15 / 60
        
        # get amount earned
        earned = time_worked * 2.5
        
        # get account balance
        balance = self.cur.execute("SELECT * FROM balance ORDER BY date DESC").fetchone()
        if balance is not None:
            balance = balance[2]
        else:
            balance = 0.00
        balance += earned
        
        # update database
        self.cur.execute("INSERT INTO punches_out VALUES (?,?)", (now, time_worked))
        self.cur.execute("INSERT INTO balance VALUES (?,?,?)", (now, time_worked, balance))
        
        self.db.commit()
        return hours_worked, earned, balance
    
    def do_punch(self, args):
        """If last punch was in, punch out. If last punch was out, punch in."""
        
        cur = self.cur
        
        last_in = cur.execute("SELECT date FROM punches_in ORDER BY date DESC").fetchone()
        last_out = cur.execute("SELECT date FROM punches_out ORDER BY date DESC").fetchone()
        
        if last_in is None:
            # no punches yet, first punch in
            print("Punching in...\nWelcome to your first day!")
            self.punch_in()
            
        elif last_out is None or last_in[0] > last_out[0]:
            # have punched in, but not out
            print("Punching out...")
            hours_worked, earned, balance = self.punch_out(last_in)
            
            print("You worked %f hours this shift" % hours_worked)
            print("You earned $%.2f this shift" % earned)
            print("Your account balance is now $%.2f" % balance)
        else:
            print("Punching in...")
            self.punch_in()
    
    def do_balance(self, args):
        """Get current account balance"""
        
        balance = self.cur.execute("SELECT * FROM balance ORDER BY date DESC").fetchone()[2]
        print("Your current balance is $%.2f" % balance)
        
    def do_withdraw(self, args):
        """Withdraw from your account"""
        
        amount = float(input("How much? "))
        
        balance = self.cur.execute("SELECT * FROM balance ORDER BY date DESC").fetchone()[2]
        if amount > balance:
            print("Insufficient funds! Withdrawl canceled.")
            print("Use the `balance` command to check your account balance")
            return
        
        balance -= amount
        now = time()
        self.cur.execute("INSERT INTO withdrawls VALUES (?,?)", (now, amount))
        self.cur.execute("INSERT INTO balance VALUES (?,?,?)", (now, 0.0, balance))
        self.db.commit()
        print("Withdrawl complete. Your new balance is $%.2f" % balance)
    
    def do_quit(self, args):
        self.db.commit()
        self.db.close()
        sys.exit(0)
        
    def preloop(self):
        db = sqlite3.connect('payroll.db')
        cur = db.cursor()
        
        cur.execute(tbl_punches_in)
        cur.execute(tbl_punches_out)
        cur.execute(tbl_withdrawls)
        cur.execute(tbl_balance)
        
        db.commit()
        
        self.db = db
        self.cur = cur
        

if __name__ == '__main__':
    PayrollShell().cmdloop()