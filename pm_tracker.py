#!/usr/bin/env python3

import cmd
import sys
import os
import csv
import json
import os.path

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
        while not choice or choice not in 'BMCEX':
            print("\nView what?")
            print("==========\n")
            
            print("B - Basic info (machine number, smid, location...)")
            print("M - Manufacturing info (serial, vendor, DOM...)")
            print("C - Configuration (par, paytable, max bet...)")
            print("E - Eproms")
            
            print("\nX - Return to machine commands")
            
            choice = input('??? ').upper()
            
        if choice == 'B':
            # Machine number
            # Slot Master ID
            # Seal/asset number
            # Location
            # DPU and box
            print('\n\x1b[32;1m' + m.description + '\x1b[0m')
            print('-' * len(m.description))
            
            rows = []
            rows.append(['slot_num', 'smid', 'seal_num'])
            rows.append(['loc_row', 'oid_dpu', None, 'oid_box'])
            display_record(m, rows)
            
        elif choice == 'M':
            # Serial number
            # Manufacturer/vendor
            # Manufacture date
            # Game style (video or reel)
            # Model name
            # Cabinet style (flat, upright, slant, novelty, etc.)
            # Cabinet color
            print('\n\x1b[32;1m' + m.description + '\x1b[0m')
            print('-' * len(m.description))
            
            rows = []
            rows.append(['serial_num', 'mftr', 'mftr_date'])
            rows.append(['style', 'model', 'cabinet', 'color'])
            display_record(m, rows)
            
        elif choice == 'C':
            # Accounting denom
            # Multidenom denoms
            # Par
            # Number of paylines
            # Max bet
            # Paytable
            # Progressive info
            # Type code
            # Multigame flag
            print('\n\x1b[32;1m' + m.description + '\x1b[0m')
            print('-' * len(m.description))
            
            rows = []
            rows.append(['type_code', 'acct_denom', 'md_denoms'])
            rows.append(['paytable', 'par', 'maxbet', 'paylines'])
            rows.append(['progressive', None, 'multi_game'])
            display_record(m, rows)
            
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
        db = setup_db(self.data_dir)
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
    """Retrieve and render the first row of a set"""
    rows = db_set.select()
    this_row = rows.render(0)
    this_row._db = rows.db
    
    # get original field objects for labels, type, etc.
    this_row._fields = dict()
    for col in rows.colnames:
        table, field = col.split('.')
        table = table.strip('"')
        field = field.strip('"')
        this_row._fields[field] = this_row._db[table][field]
        
    return this_row
    
    
def display_record(src, fmt, data_color='\x1b[32;1m', label_color='\x1b[0m', sep=':'):
    """
    Select and display given fields of a single record.
    
    `src` is the source data as a pydal Row object.
    `fmt` is a list of lists, where each sublist is a display row containing keys into `src`
    
    `data_color` is an ANSI escape sequence for coloring data (default bright green)
    `label_color` is an ANSI escape sequence for coloring the labels (default white)
    `sep` is the separator between label and data
    
    For each display row, this function will use each item as a key in `src` and display
    `src[item].label` and `src[item]` separated by `sep` and a space. If `item` is None,
    then it will insert an extra tab character.
    """
    
    for r in fmt:
        disp_row = ''
        for k in r:
            if k is not None:
                label = src._fields[k].label
                disp_row += label_color + label + sep + ' '
                disp_row += data_color + str(src[k])
            disp_row += '\t'
        print(disp_row, '\x1b[0m')

    
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


def setup_db(data_dir):
    cwd = os.getcwd()
    os.chdir(data_dir)
    
    db = DAL("sqlite://poorbart.db", folder=data_dir)
    
    def rows_render(f, v, r):
        # why the fuck isn't this in the base DAL already?
        # it's in the unit tests instead
        if callable(f.represent):
            return f.represent(v, r)
        else:
            return str(v)
    
    # required for rows.render() to use fields' represent attribute
    db.representers['rows_render'] = rows_render
    
    db.define_table('all_machines',
        Field('on_floor', 'boolean', required=True, label='On floor', represent=lambda v,r: 'Y' if v else 'N'),
        Field('smid', 'integer', required=True, unique=True, label='SMID'),
        Field('slot_num', 'integer', required=True, label='Machine number'),
        Field('loc_casino', 'integer', label='Casino', represent=lambda v,r: '%02i'%v),
        Field('loc_row', label='Row'),
        Field('oid_dpu', 'integer', label='DPU'),
        Field('oid_box', 'integer', label='Sentinel'),
        Field('acct_denom', 'double', required=True, default=0.01, label='Meter denom', represent=lambda v,r: '$%#.2f'%v),
        Field('mktg_id', label='Marketing ID'),
        Field('md_denoms', 'list:double', label='Denoms', represent=lambda v,r: ' '.join(['%#.2f'%i for i in v])),
        Field('par', 'double', label='Par', represent=lambda v,r: '%#.3f%%'%v),
        Field('description', label='Theme'),
        Field('game_series', label='Game series'),
        Field('paylines', 'integer', label='Paylines'),
        Field('reels', 'integer', label='Reels'),
        Field('maxbet', 'integer', label='Max bet'),
        Field('eproms', 'json'),
        Field('paytable', label='Paytable'),
        Field('progressive', label='Progressive'),
        Field('type_code', 'integer', label='Type code'),
        Field('style', default='V', length=1, label='Game style'),
        Field('mftr', label='Vendor'),
        Field('model', label='Model'),
        Field('cabinet', label='Cabinet style'),
        Field('color', label='Color'),
        Field('mftr_date', label='DOM'),
        Field('serial_num', required=True, label='Serial number'),
        Field('seal_num', 'integer', label='Seal number'),
        Field('multi_denom', 'boolean', required=True, label='Multidenom', represent=lambda v,r: 'Y' if v else 'N'),
        Field('multi_game', 'boolean', required=True, label='Multigame', represent=lambda v,r: 'Y' if v else 'N'),
        Field('bv_model', required=True, label='BV model'),
        Field('bv_firmware', required=True, label='BV firmware'),
        Field('printer_model', required=True, label='Printer model'),
        Field('printer_firmware', required=True, label='Printer firmware'),
        Field('board_level', label='Board level'),
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
    if os.path.isfile('pm_config.conf'):
        data_dir = json.loads(open('pm_config.conf').read())['data_dir']
    else:
        data_dir = 'U:\floor_data'
    col.init()
    bart = PoorBart()
    bart.data_dir = data_dir
    bart.cmdloop()
