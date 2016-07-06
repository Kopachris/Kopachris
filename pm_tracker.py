#!/usr/bin/env python3

import cmd
import sys
import os
import csv

import colorama as col
from pydal import DAL, Field
from datetime import datetime
from pathlib import Path


class PoorBart(cmd.Cmd):
    intro = "Welcome to a poor substitute for Oasis BlackBart\n"
    
    def preloop(self):
        self.db = setup_db()
        
    def do_exit(self, args):
        sys.exit()
        
    def do_import(self, args):
        """Import .csv files to the database."""
        
        print("Import .CSV")
        print("===========\n")
        
        print("Import what?")
        print("I - machine info")
        print("M - maintenance log")
        
        choice = ''
        while choice not in ('I', 'M'):
            choice = input(' ? ').upper()
            
        if choice == 'I':
            files = list(list_files())
            file_idx = int(input("Which file? ")) - 1
            r_added, r_updated = import_machines(self.db, files[file_idx])
            
    
    def do_addtech(self, args):
        """Add a new technician to the database."""
        
        print("Create new technician")
        print("=====================\n")
        
        sn, fn = '', ''
        while not sn:
            sn = input("Short name: ")
        while not fn:
            fn = input("Full name: ")
        nick = input("Nickname (optional): ")
        
        db = self.db
        try:
            id = db.tech_names.insert(short_name=sn, full_name=fn, nickname=nick)
            db.commit()
            print("Added new technician, id #%i" % id)
        except:
            print("Could not add new technician or technician already exists with that short name.")


def import_machines(db, f):
    """Import machine info from a .csv file into the database.
    
    Args:
        db - DAL object represting the database connection
        f - Path object with the .csv file location
    """
    
    with f.open() as csvfile:
        csvreader = csv.DictReader(csvfile)
        for r in csvreader:
            db.all_machines.update_or_insert(
                db.all_machines.smid == r['SlotMastID'],
                on_floor=r['OnFloor'],
                smid=r['SlotMastID'],
                slot_num=r['SlotNumber'],
                loc_casino=r['
            )
            
            
def list_files(ftype='csv'):
    """Print a list of files in the current directory tree
    with the given file extension (default='csv').
    """
    
    p = Path('.')
    files = p.glob('**/*.' + ftype)
    for i, f in enumerate(files, 1):
        print("%i - %s" % (i, f))
        
    return files


def setup_db():
    cwd = os.getcwd()
    os.chdir(r"U:\floor_data")
    
    db = DAL("sqlite://poorbart.db", folder=r"U:\floor_data")
    
    db.define_table('all_machines',
        Field('on_floor', 'boolean', required=True),
        Field('smid', 'integer', required=True, unique=True),
        Field('slot_num', 'integer', required=True),
        Field('loc_casino', 'integer'),
        Field('loc_row'),
        Field('oid_poller', 'integer'),
        Field('oid_dpu', 'integer'),
        Field('oid_box', 'integer'),
        Field('acct_denom', 'float', required=True, default=0.01),
        Field('mktg_id'),
        Field('md_denoms'),
        Field('par', 'float'),
        Field('description'),
        Field('paylines', 'integer'),
        Field('reels', 'integer'),
        Field('maxbet', 'integer'),
        Field('eproms', 'json'),
        Field('paytable'),
        Field('progressive'),
        Field('notes', 'text'),
        Field('type_code', 'integer'),
        Field('style', default='V'),
        Field('mftr'),
        Field('model'),
        Field('cabinet'),
        Field('color'),
        Field('mftr_date', 'date'),
        Field('serial_num', required=True),
        Field('seal_num', 'integer'),
        Field('multi_denom', 'boolean', required=True),
        Field('multi_game', 'boolean', required=True),
        Field('bv_model', required=True),
        Field('bv_firmware', required=True),
        Field('printer_model', required=True),
        Field('printer_firmware', required=True),
    )
    db.define_table('conversions',
        Field('conv_date', 'date', default=datetime.today(), required=True),
        Field('new_num', 'reference all_machines', required=True),
        Field('old_num', 'reference all_machines', required=True),
    )
    db.define_table('moves',
        Field('move_date', 'date', default=datetime.today(), required=True),
        Field('machine', 'reference all_machines', required=True),
        Field('new_loc', required=True),
        Field('old_loc', required=True),
    )
    db.define_table('tech_names',
        Field('short_name', required=True, unique=True),
        Field('full_name', required=True),
        Field('nickname'),
    )
    db.define_table('pm_areas',
        Field('tech_name', 'reference tech_names', required=True),
        Field('row', required=True),
    )
    db.define_table('pm_activity',
        Field('code_date', 'datetime', required=True),
        Field('machine', 'reference all_machines', required=True),
        Field('tech_name', 'reference tech_names'),
        Field('pm_code', 'integer', required=True),
    )
    
    return db
        
        
if __name__ == '__main__':
    col.init()
    bart = PoorBart()
    bart.cmdloop()