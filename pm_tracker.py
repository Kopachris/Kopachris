#!/usr/bin/env python3

import cmd
import sys
import os
import csv
import json

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
            machine = dict()
            
            machine['on_floor'] = True if r['OnFloor'] == 'Y' else False
            machine['smid'] = int(r['SlotMastID'])
            machine['slot_num'] = int(r['SlotNumber'])
            
            # LocationString like '01 A-02-01'
            location = r['LocationString'].split()
            machine['loc_casino'] = int(location[0])
            machine['loc_row'] = location[1]
            
            # OasisID like '01-45-10'
            oasis_id = r['OasisID'].split('-')
            machine['oid_dpu'] = int(oasis_id[1])
            machine['oid_box'] = int(oasis_id[2])
            
            machine['acct_denom'] = float(r['Denom'].strip('$'))
            machine['mktg_id'] = r['MktgID']
            
            # MD Denominations like '.05/.25/.50/1.00'
            machine['md_denoms'] = [float(x) for x in r['MD Denominations'].split('/']
            
            machine['par'] = float(r['Par'].strip('%'))
            machine['description'] = r['Description']
            machine['game_series'] = r['Game Series']
            machine['paylines'] = int(r['# Paylines'])
            machine['reels'] = int(r['# Reels'])
            machine['maxbet'] = int(r['# Coins'])  # credits
            
            # EPROMs and software versions are under multiple fields in Oasis
            # we want to compress them to one JSON object, except BV and printer
            eproms = dict()
            eprom_fields = (
                'Eprom #1',
                'Eprom #2',
                'Eprom #3',
                'Eprom #4',
                'Game Software',
                'Base Software',
                'OS Software',
                'Video Software',
                'Sound Software',
                'Eprom 6',
                'Boot Eprom',
                'SPC Version',
                'Jurisdiction Software',
                'Game Software 2',
                'Game Software 3',
                'Game Software 4',
                'Game Software 5',
                'OS Software 2',
                'OS Software 3',
            )
            for field in eprom_fields:
                if r[field]:
                    eproms[field] = r[field]
            machine['eproms'] = json.dumps(eproms)
            
            machine['paytable'] = r['Paytable']
            machine['progressive'] = r['Prog %']  # TODO parse this?
            machine['type_code'] = int(r['Slot Type ID'])
            machine['style'] = r['Basic Style']
            machine['mftr'] = r['Mftr']
            machine['model'] = r['Model']
            machine['cabinet'] = r['Cabinet']
            machine['color'] = r['Color/Laminate']
            
            # DOM like mm/dd/yyyy
            machine['mftr_date'] = datetime.strptime(r['DOM'], '%m/%d/%Y')
            
            machine['serial_num'] = r['SerialNumber']
            machine['seal_num'] = int(r['SealNumber'])
            
            machine['multi_denom'] = True if r['Multi Denom'] == 'Y' else False
            machine['multi_game'] = True if r['Multi Game'] == 'Y' else False
            
            # Commonly used: I100 SS and iVision with various casing
            # UBA and WBA always like UBA10 03
            machine['bv_model'] = 'iVizion' if r['BV Eprom'].lower().startswith('i') else r['BV Eprom']
            machine['bv_firmware'] = r['BV ID #']
            
            machine['printer_model'] = r['Printer Type']
            machine['printer_firmware'] = r['Printer Firmware']
            machine['board_level'] = r['Board Level']
            
            db.all_machines.update_or_insert(db.all_machines.smid == machine['smid'], **machine)
            
            
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
        Field('oid_dpu', 'integer'),
        Field('oid_box', 'integer'),
        Field('acct_denom', 'double', required=True, default=0.01),
        Field('mktg_id'),
        Field('md_denoms', 'list:double'),
        Field('par', 'double'),
        Field('description'),
        Field('game_series'),
        Field('paylines', 'integer'),
        Field('reels', 'integer'),
        Field('maxbet', 'integer'),
        Field('eproms', 'json'),
        Field('paytable'),
        Field('progressive'),
        Field('type_code', 'integer'),
        Field('style', default='V', length=1),
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
        Field('board_level'),
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
    db.define_table('machine_notes',
        Field('note_added', 'datetime', required=True, default=datetime.today()),
        Field('machine', 'reference all_machines', required=True),
        Field('added_by', 'reference tech_names', required=True),
        Field('note', 'text'),
    )
    
    return db
        
        
if __name__ == '__main__':
    col.init()
    bart = PoorBart()
    bart.cmdloop()
