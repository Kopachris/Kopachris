#!/usr/bin/env python3

import cmd
import sys
import os
import csv

import colorama as col
from pydal import DAL, Field
from datetime import datetime
from pathlib import Path


class MachineCmd(cmd.Cmd):
    prompt = "(machine)"
    stop = False
    
    def preloop(self):
        fail = False
        if not hasattr(self, 'db'):
            print("Missing database!")
            fail = True
        if not hasattr(self, 'machine'):
            print("No machine selected!")
            fail = True
            
        if fail:
            self.close()
            return
        
        self.prompt = "(machine) %i >> " % self.machine.slot_num
    
    def postcmd(self, stop, line):
        if self.stop:
            return True
    
    def do_main(self, args):
        self.stop = True
        
    def do_back(self, args):
        self.stop = True
        
    def do_view(self, args):
        """View machine info"""
        
        m = self.machine
        
        choice = args.upper() if args else ''
        while choice not in 'BMEX':
            print("\nView what?")
            print("==========\n")
            
            print("B - Basic info (machine number, smid, location...)")
            print("M - Manufacturing info (serial, vendor, DOM...)")
            print("E - Eproms")
            
            print("\nX - Return to machine commands")
            
            choice = input('??? ').upper()
            
        if choice == 'B':
            print('\n\x1b[32;1m' + m.description + '\x1b[0m')
            print('-' * len(m.description))
            print("Machine number: \x1b[32;1m%i\t\x1b[0mSMID: \x1b[32;1m%i\t\x1b[0mSeal number: \x1b[32;1m%i\x1b[0m" % (m.slot_num, m.smid, m.seal_num))
            print("Location: \x1b[32;1m%s\t\x1b[0mDPU: \x1b[32;1m%i\t\t\x1b[0mSentinel: \x1b[32;1m%i\n\x1b[0m" % (m.loc_row, m.oid_dpu, m.oid_box))
            
        elif choice == 'M':
            print('\n\x1b[32;1m' + m.description + '\x1b[0m')
            print('-' * len(m.description))
            print("Serial number: \x1b[32;1m%s\t\x1b[0mVendor: \x1b[32;1m%s\t\x1b[0mDOM: \x1b[32;1m%s\x1b[0m" % (m.serial_num, m.mftr, m.mftr_date))
            print("Style: \x1b[32;1m%s\t\x1b[0mModel: \x1b[32;1m%s\t\x1b[0mCabinet: \x1b[32;1m%s\t\x1b[0mColor: \x1b[32;1m%s\n\x1b[0m" % (m.style, m.model, m.cabinet, m.color))
            
        elif choice == 'E':
            print('\n\x1b[32;1m' + m.description + '\x1b[0m')
            print('-' * len(m.description))
            
            for k, v in m.eproms.items():
                print("%s: \x1b[32;1m%s\x1b[0m" % (k, v))
            print('')
            
        elif choice == 'X':
            return


class PoorBart(cmd.Cmd):
    intro = "Welcome to a poor substitute for Oasis BlackBart\n"
    
    def preloop(self):
        db = setup_db()
        self.on_floor = db(db.all_machines.on_floor == True).count()
        self.intro = self.intro + "%i machines currently on the floor.\n" % self.on_floor
        self.db = db
        
    def postcmd(self, stop, line):
        db = self.db
        self.on_floor = db(db.all_machines.on_floor == True).count()
        self.intro = self.intro + "%i machines currently on the floor.\n" % self.on_floor
    
    def do_exit(self, args):
        sys.exit()
        
    def do_machine(self, args):
        """
Select a machine that's on the floor and enter machine commands

Usage:
    machine             prompt for a machine number
    machine 1234        select machine number 1234
    
    machine -s 6230     select machine with SMID 6230
    machine --smid 6230
    
    machine -l A-02-02  select machine at location A-02-02
    machine --location A-02-02
        """

        machs = self.db.all_machines
        db = self.db
        q = (machs.on_floor == True)
        
        if args:
            args = args.split()
        else:
            while not args.isnumeric():
                args = input("Machine number? ")
        
        if len(args) == 1 and args[0].isnumeric():
            machine = int(args[0])
            q &= (machs.slot_num == machine)
        elif args[0] == '-s' or args[0] == '--smid':
            if args[1].isnumeric():
                smid = int(args[1])
                q &= (machs.smid == smid)
            else:
                print("Invalid argument for SMID")
                return
        elif args[0] == '-l' or args[0] == '--location':
            q &= (machs.loc_row == args[1])
        
        this_machine = get_one(db(q))
        if not this_machine:
            print("Machine not found")
            return
        
        machine_cmd = MachineCmd()
        machine_cmd.machine = this_machine
        machine_cmd.db = db
        machine_cmd.cmdloop()
    
    def do_import(self, args):
        """Import .csv files to the database."""
        
        print("Import .CSV")
        print("===========\n")
        
        print("Import what?")
        print("I - machine info")
        print("M - maintenance log")
        
        choice = ''
        while choice not in ('I', 'M'):
            choice = input('??? ').upper()
            
        if choice == 'I':
            files = list_files()
            file_idx = int(input("Which file? ")) - 1
            r_added, r_updated = import_machines(self.db, files[file_idx])
            
            print("Added %i and updated %i machines" % (r_added, r_updated))
            
    
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
            
    do_quit = do_exit


def get_one(db_set):
    return db_set.select().first()

    
def import_machines(db, f):
    """
    Import machine info from a .csv file into the database.
    
    Args:
        db - DAL object represting the database connection
        f - Path object with the .csv file location
    """
    
    with f.open() as csvfile:
        csvreader = csv.DictReader(csvfile)
        updated_rows = 0
        inserted_rows = 0
        machs = db.all_machines
        
        for r in csvreader:
            if not r['SlotMastID']: continue  # get around blank rows
            smid = int(r['SlotMastID'])
            
            existing_row = db(machs.smid == smid).select().first()
            if existing_row:
                print('Updating machine ', r['SlotNumber'])
            else:
                print('Importing machine ', r['SlotNumber'])
                
            machine = dict()
            
            machine['on_floor'] = True if r['OnFloor'] == 'Y' else False
            
            machine['smid'] = smid
            machine['slot_num'] = int(r['SlotNumber'])
            
            # LocationString like '01 A-02-01'
            location = r['LocationString'].split()
            machine['loc_casino'] = int(location[0])
            machine['loc_row'] = location[1]
            
            # OasisID like '01-45-10'
            oasis_id = r['OasisId'].split('-')
            machine['oid_dpu'] = int(oasis_id[1])
            machine['oid_box'] = int(oasis_id[2])
            
            machine['acct_denom'] = float(r['Denom'].strip('$'))
            machine['mktg_id'] = r['MktgId']
            
            # MD Denominations like '.05/.25/.50/1.00'
            machine['md_denoms'] = [float(x.strip('$')) for x in r['MD Denominations'].split('/')]
            
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
                'Boot EPROM',
                'SPC Version',
                'Jurisdictional Software',
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
            machine['eproms'] = eproms
            
            machine['paytable'] = r['Paytable']
            machine['progressive'] = r['Prog %']  # TODO parse this?
            machine['type_code'] = int(r['Slot Type ID'])
            machine['style'] = r['Basic Style']
            machine['mftr'] = r['Mftr']
            machine['model'] = r['Model']
            machine['cabinet'] = r['Cabinet']
            machine['color'] = r['Color/Laminate']
            machine['mftr_date'] = r['DOM']
            machine['serial_num'] = r['SerialNumber']
            machine['seal_num'] = int(r['SealNumber']) if r['SealNumber'].isnumeric() else None
            
            machine['multi_denom'] = True if r['Multi Denom'] == 'Y' else False
            machine['multi_game'] = True if r['Multi Game'] == 'Y' else False
            
            # Commonly used: I100 SS and iVision with various casing
            # UBA and WBA always like UBA10 03
            machine['bv_model'] = 'iVizion' if r['BV Eprom'].lower().startswith('i') else r['BV Eprom']
            machine['bv_firmware'] = r['BV ID #']
            
            machine['printer_model'] = r['Printer Type']
            machine['printer_firmware'] = r['Printer Firmware']
            machine['board_level'] = r['Board Level']
            
            if existing_row:
                machs[existing_row.id] = machine
                updated_rows += 1
            else:
                machs[0] = machine
                inserted_rows += 1
            
            db.commit()
            
    return inserted_rows, updated_rows
            
            
def list_files(ftype='csv'):
    """Print a list of files in the current directory tree
    with the given file extension (default='csv').
    """
    
    p = Path('.')
    files = list(p.glob('**/*.' + ftype))
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
        Field('mftr_date'),
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
