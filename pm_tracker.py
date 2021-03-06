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
from dateutil.parser import parse as parse_dt
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
        
    def do_view(self, args, show_menu=True):
        """View machine info"""
        
        m = self.machine
        c = self.cabinet
        
        if show_menu:
            print("\nView what?")
            print("==========\n")
            
            print("B - Basic info (machine number, smid, location...)")
            print("M - Manufacturing info (serial, vendor, DOM...)")
            print("C - Configuration (par, paytable, max bet...)")
            print("E - Eproms")
            print("H - History")
            
            print("\nX - Return to machine commands")
        
        choice = args.upper() if args else ''
        while not choice or choice not in 'BMCEHX':
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
            
            return 'B'
            
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
            rows.append(['model', 'cabinet', 'color'])
            display_record(c, rows)
            
            return 'M'
            
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
            
            return 'C'
            
        elif choice == 'E':
            print('\n\x1b[32;1m' + m.description + '\x1b[0m')
            print('-' * len(m.description))
            
            for k, v in m.eproms.items():
                print("%s: \x1b[32;1m%s\x1b[0m" % (k, v))
            print('')
            
            return 'E'
            
        elif choice == 'H':
            db = self.db
            machs = db.all_machines
            cons = db.conversions
            moves = db.moves
            pms = db.pm_activity
            techs = db.tech_names
            
            con_to = db(cons.old_num == m.id).select().first()
            con_from = db(cons.new_num == m.id).select().first()
            
            moves = db(moves.machine == m.id).select()
            
            last_200 = db((pms.pm_code == 200) & (pms.machine == m.cabinet)).select().last()
            last_201 = db((pms.pm_code == 201) & (pms.machine == m.cabinet)).select().last()
            last_203 = db((pms.pm_code == 203) & (pms.machine == m.cabinet)).select().last()
            
            print('\n\x1b[32;1m' + m.description + '\x1b[0m')
            print('-' * len(m.description))
            
            rows = []
            rows.append(['slot_num', 'smid', 'seal_num'])
            rows.append(['loc_row', 'oid_dpu', None, 'oid_box'])
            display_record(m, rows)
            
            # color yellow
            print('\x1b[33;1m')
            
            if not con_to and not con_from:
                print("No conversions")
            else:
                if con_to:
                    to_machine = machs[con_to.new_num].slot_num
                    print("Converted to %s on %s" % (to_machine, con_to.conv_date))
                if con_from:
                    from_machine = machs[con_from.old_num].slot_num
                    print("Converted from %s on %s" % (from_machine, con_from.conv_date))
                    
            if not len(moves):
                print("No moves")
            else:
                for move in moves:
                    print("Moved from %s to %s on %s" % (move.old_loc, move.new_loc, move.move_date))
                    
            if last_200:
                tech = db(techs.id == last_200.tech_name).select().first()
                print("Last PM3 was on %s by %s" % (last_200.code_date, tech.full_name))
            else:
                print("No PM3's")
                
            if last_201:
                tech = db(techs.id == last_201.tech_name).select().first()
                print("Last PM2 was on %s by %s" % (last_201.code_date, tech.full_name))
            else:
                print("No PM2's")
                
            if last_203:
                tech = db(techs.id == last_203.tech_name).select().first()
                print("Last button check was on %s by %s" % (last_203.code_date, tech.full_name))
            else:
                print("No button checks")
                
            # clear formatting
            print('\x1b[0m')
            
            return 'H'
            
        elif choice == 'X':
            return 'X'


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
        
    do_quit = do_exit
        
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
        cabs = self.db.cabinets
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
            
        this_cabinet = get_one(db(cabs.id == this_machine.cabinet))
        
        machine_cmd = MachineCmd()
        machine_cmd.machine = this_machine
        machine_cmd.cabinet = this_cabinet
        machine_cmd.db = db
        
        choice = ''
        while choice != 'X':
            choice = machine_cmd.do_view('', show_menu=False if choice else True)
        
    def do_search(self, args):
        """Search for machines by description."""
        
        if not args:
            print("No search term specified!")
            return
        
        db = self.db
        machs = db.all_machines
        
        # split search term into individual words and create db query
        search_terms = args.split()
        q = machs.description.contains(search_terms[0])
        if len(search_terms) > 1:
            for term in search_terms[1:]:
                # query should return machines containing any term in description
                q |= machs.description.contains(term)
                
        results = db(q).select(machs.slot_num, machs.loc_row, machs.description)
        
        if not len(results):
            print("No results")
            return
        
        # TODO rank/sort by number of terms present?
        
        print("Machine\t\tRow\t\tDescription")
        print("-------\t\t---\t\t-----------")
        
        for r in results:
            print("%i\t\t%s\t\t%s" % (r.slot_num, r.loc_row, r.description))
            
    def do_move(self, args):
        """Move existing machine to a new location"""
        
        db = self.db
        
        if not args.isnumeric():
            machine = int(input("Machine number? "))
        else:
            machine = int(args)
            
        q = db.all_machines.on_floor == True
        q &= db.all_machines.slot_num == machine
        
        m = get_one(db(q))
        if not m:
            print("Machine not found!")
            return
            
        # display basic machine info
        print('\n\x1b[32;1m' + m.description + '\x1b[0m')
        print('-' * len(m.description))
        
        rows = []
        rows.append(['slot_num', 'smid', 'seal_num'])
        rows.append(['loc_row', 'oid_dpu', None, 'oid_box'])
        display_record(m, rows)
        print('')
        
        new_row = input("New location? ")
        new_dpu = int(input("New DPU? "))
        new_box = int(input("New box? "))
        
        if not new_row and not new_dpu and not new_box:
            print("No changes made.")
            return
            
        if new_row:
            db.moves.insert(machine=m.id, new_loc=new_row, old_loc=m.loc_row)
            m.update_record(loc_row=new_row)
            
        if new_dpu:
            m.update_record(oid_dpu=new_dpu)
            
        if new_box:
            m.update_record(oid_box=new_box)
            
        db.commit()
        
        print("Updated machine.")
    
    def do_import(self, args):
        """Import .csv files to the database."""
        
        print("Import .CSV")
        print("===========\n")
        
        print("Import what?")
        print("I - machine info")
        print("M - maintenance log")
        
        choice = 'X'
        while choice not in 'IM':
            choice = input('??? ').upper()
            
        if choice == 'I':
            files = list_files()
            file_idx = int(input("Which file? ")) - 1
            r_added, r_updated = import_machines(self.db, files[file_idx])
            
            print("Added %i and updated %i machines" % (r_added, r_updated))
        elif choice == 'M':
            files = list_files()
            file_idx = int(input("Which file? ")) - 1
            r_added = import_maint(self.db, files[file_idx])
            
            print("Added %i maintenance records" % r_added)
            
    def do_conversion(self, args):
        """Convert a machine"""
        
        db = self.db
        machs = db.all_machines
        cons = db.conversions
        old_m = ''
        new_m = ''
        
        while not old_m.isnumeric():
            old_m = input("Old Machine #? ")
        old_m = int(old_m)
        
        old_machine = db(machs.slot_num == old_m)
        if old_machine.isempty():
            print("Old machine not in database.")
            return
            
        old_machine = get_one(old_machine)
        
        # display basic machine info
        print('\n\x1b[32;1m' + str(old_machine.description) + '\x1b[0m')
        print('-' * len(str(old_machine.description)))
        
        rows = []
        rows.append(['slot_num', 'smid', 'seal_num'])
        rows.append(['loc_row', 'oid_dpu', None, 'oid_box'])
        display_record(old_machine, rows)
        print('')
        
        while not new_m.isnumeric():
            new_m = input("New Machine #? ")
        new_m = int(new_m)
            
        new_machine = db(machs.slot_num == new_m)
        if new_machine.isempty():
            # copy data from old machine
            print("Copying old machine")
            smid = int(input("New SMID? "))
            
            new_data = old_machine.as_dict()
            
            del new_data['id']
            new_data['smid'] = smid
            new_data['slot_num'] = new_m
            
            new_id = machs.insert(**new_data)
        else:
            new_id = get_one(new_machine).id
        
        old_id = old_machine.id
        
        conv_date = ''
        while not conv_date:
            try:
                conv_date = parse_dt(input("Conversion date? "))
            except ValueError:
                print("Unable to parse date, try yyyy/mm/dd format")
                conv_date = ''
            
        cons.insert(conv_date=conv_date, new_num=new_id, old_num=old_id)
        db.commit()
        print("Machine converted")
            
    def do_final(self, args):
        """Take a machine off the floor"""
        
        db = self.db
        machs = db.all_machines
        finals = db.finals
        
        while not args.isnumeric():
            args = input("Machine #? ")
        args = int(args)
        
        machine = db((machs.slot_num == args) & (machs.on_floor == True))
        if machine.isempty():
            print("Machine not found.")
            return
            
        machine = get_one(machine)
            
        # display basic machine info
        print('\n\x1b[32;1m' + machine.description + '\x1b[0m')
        print('-' * len(machine.description))
        
        rows = []
        rows.append(['slot_num', 'smid', 'seal_num'])
        rows.append(['loc_row', 'oid_dpu', None, 'oid_box'])
        display_record(machine, rows)
        print('')
            
        final_date = ''
        while not final_date:
            try:
                final_date = parse_dt(input("Final date? "))
            except ValueError:
                print("Unable to parse date, try yyyy/mm/dd format")
                final_date = ''
        
        machine.update_record(on_floor=False, loc_casino=0, loc_row='', oid_dpu=0, oid_box=0)
        finals.insert(final_date=final_date, machine=machine.id)
        
        db.commit()
        print("Machine taken off floor.")
            
    def do_addmachine(self, args):
        """Manually add a machine to the database."""
        
        db = self.db
        machs = db.all_machines
        cabs = db.cabinets
        
        print("Add new machine")
        print("===============\n")
        
        smid = slot_num = serial_num = ''
        while not smid.isnumeric():
            smid = input("Slot Master ID: ")
        while not slot_num.isnumeric():
            slot_num = input("Machine #: ")
        while not serial_num:
            serial_num = input("Serial number: ")
            
        smid = int(smid)
        slot_num = int(slot_num)
            
        # get cabinet ID for that serial number if it exists,
        # otherwise insert new cabinet
        cab = db(cabs.serial_num == serial_num)
        if cab.isempty():
            cab_id = cabs.insert(serial_num=serial_num)
        else:
            cab_id = cab.select().first().id
            
        # can't have duplicate smid or machine number
        chk_smid = db(machs.smid == smid).isempty()
        chk_slot_num = db((machs.slot_num == slot_num) & (machs.on_floor == True)).isempty()
        if not chk_smid:
            print("Machine already exists with that SMID")
            return
        if not chk_slot_num:
            print("Machine already exists on floor with that machine number")
            return
            
        machs.insert(on_floor=False, smid=smid, slot_num=slot_num, cabinet=cab_id)
        db.commit()
        print("Added machine")
        
    
    def do_addtech(self, args):
        """Add a new technician to the database."""
        
        print("Add new technician")
        print("==================\n")
        
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
            
    def do_edittech(self, args):
        """Edit an existing technician."""
        
        db = self.db
        
        while not args:
            args = input("Existing tech short name: ")
            
        existing_tech = db(db.tech_names.short_name.like(args)).select().first()
        
        if existing_tech:
            print("Current short name: ", existing_tech.short_name)
            print("Current full name: ", existing_tech.full_name)
            print("Current nickname: ", existing_tech.nickname)
        else:
            print("Tech not found.")
            return
            
        new_sn = input("New short name? ") or existing_tech.short_name
        new_fn = input("New full name? ") or existing_tech.full_name
        new_nick = input("New nickname? ") or existing_tech.nickname
        
        existing_tech.update_record(short_name=new_sn, full_name=new_fn, nickname=new_nick)
        db.commit()
        
        print("Updated.")
    
    def do_setarea(self, args):
        """Set PM area for a tech"""
        
        db = self.db
        
        while not args:
            args = input("Which tech? ")
            
        tech = get_one(db(db.tech_names.short_name == args))
        if tech is None:
            print("Tech not found.")
            return
            
        pm_rows = ''
        while not pm_rows:
            pm_rows = input("Enter rows assigned to this tech, separated by commas: ").split(',')
            
        # first clear currently assigned rows
        area = db(db.pm_areas.tech_name == tech.id)
        if not area.isempty():
            area = area.select()
            for r in area:
                r.delete_record()
                
            db.commit()
        
        # then add rows
        db.pm_areas.bulk_insert([{'tech_name': tech.id, 'row': r} for r in pm_rows])
        db.commit()
        print("Done.")
        
    def do_get_nonexist(self, args):
        """Generate a report of rows which are assigned to a tech but don't actually exist."""
        
        db = self.db
        
        pm_areas = db().select(db.pm_areas.ALL)
        nonexist = []
        for r in pm_areas:
            if db(db.all_machines.loc_row.startswith(r.row)).isempty():
                nonexist.append(r.row)
                
        print("These rows are assigned but no longer exist:")
        print(', '.join(nonexist))
        
    def do_get_unassigned(self, args):
        """Generate a report of rows which aren't assigned to anyone."""
        
        db = self.db
        
        all_machines = db(db.all_machines.on_floor == True).select(db.all_machines.loc_row)
        all_rows = set()
        for m in all_machines:
            all_rows.add(m.loc_row.rsplit('-', maxsplit=1)[0])
            
        unassigned = []
        for r in all_rows:
            if db(db.pm_areas.row == r).isempty():
                unassigned.append(r)
                
        unassigned.sort()
        print("These rows are not assigned to anyone:")
        print(', '.join(unassigned))


def get_one(db_set):
    """Retrieve and render the first row of a set"""
    
    if db_set.isempty():
        return None
    
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

    
def import_maint(db, f):
    """
    Import maintenance log from a .csv file into the database.
    
    Args:
        db - DAL object
        f - Path object of the .csv file
    """
    
    with f.open() as csvfile:
        csvreader = csv.DictReader(csvfile)
        updated_rows = 0
        machs = db.all_machines
        cabs = db.cabinets
        pms = db.pm_activity
        techs = db.tech_names
        
        for r in csvreader:
            dt = parse_dt(r['Datetime'])
            m = int(r['Machine'])
            code = int(r['Code'])
            tech = db(techs.full_name == r['User Name']).select().first()
            cab = db(machs.slot_num == m).select(machs.cabinet).first()
            
            q = pms.code_date == dt
            q &= pms.machine == m
            q &= pms.pm_code == code
            new_row = db(q).isempty()
            
            if new_row and tech and cab:
                # if record already exists or tech not found, skip
                pms.insert(code_date=dt, machine=cab.cabinet, tech_name=tech.id, pm_code=code)
                db.commit()
                updated_rows += 1
                
        return updated_rows
    
    
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
        cabs = db.cabinets
        
        for r in csvreader:
            if not r['SlotMastID']: continue  # get around blank rows
            smid = int(r['SlotMastID'])
            
            existing_row = db(machs.smid == smid).select().first()
            if existing_row:
                print('Updating machine ', r['SlotNumber'])
            else:
                print('Importing machine ', r['SlotNumber'])
                
            existing_cab = db(cabs.serial_num == r['SerialNumber']).select().first()
                
            machine = dict()
            cabinet = dict()
            
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
            machine['seal_num'] = int(r['SealNumber']) if r['SealNumber'].isnumeric() else None
            
            if existing_cab:
                machine['cabinet'] = existing_cab.id
            else:
                cabinet['mftr'] = r['Mftr']
                cabinet['model'] = r['Model']
                cabinet['cabinet'] = r['Cabinet']
                cabinet['color'] = r['Color/Laminate']
                cabinet['mftr_date'] = r['DOM']
                cabinet['serial_num'] = r['SerialNumber']
                
                machine['cabinet'] = cabs.insert(**cabinet)
            
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
            try:
                return f.represent(v, r) if v else str(v)
            except TypeError:
                return str(v)
        else:
            return str(v)
    
    # required for rows.render() to use fields' represent attribute
    db.representers['rows_render'] = rows_render
    
    db.define_table('cabinets',
        Field('mftr', label='Vendor'),
        Field('model', label='Model'),
        Field('cabinet', label='Cabinet style'),
        Field('color', label='Color'),
        Field('mftr_date', label='DOM'),
        Field('serial_num', required=True, label='Serial number', unique=True),
    )
    
    db.define_table('all_machines',
        Field('on_floor', 'boolean', required=True, label='On floor', represent=lambda v,r: 'Y' if v else 'N'),
        Field('smid', 'integer', required=True, unique=True, label='SMID'),
        Field('slot_num', 'integer', required=True, label='Machine number'),
        Field('loc_casino', 'integer', label='Casino', default=0, represent=lambda v,r: '%02i'%v),
        Field('loc_row', label='Row', default=''),
        Field('oid_dpu', 'integer', label='DPU', default=0),
        Field('oid_box', 'integer', label='Sentinel', default=0),
        Field('acct_denom', 'double', required=True, default=0.01, label='Meter denom', represent=lambda v,r: '$%#.2f'%v),
        Field('mktg_id', label='Marketing ID'),
        Field('md_denoms', 'list:double', label='Denoms', represent=lambda v,r: ' '.join(['%#.2f'%i for i in v])),
        Field('par', 'double', label='Par', represent=lambda v,r: '%#.3f%%'%v),
        Field('description', label='Theme', default=''),
        Field('game_series', label='Game series', default=''),
        Field('paylines', 'integer', label='Paylines', default=1),
        Field('reels', 'integer', label='Reels', default=3),
        Field('maxbet', 'integer', label='Max bet', default=2),
        Field('eproms', 'json'),
        Field('paytable', label='Paytable', default=''),
        Field('progressive', label='Progressive', default=''),
        Field('type_code', 'integer', label='Type code', default=0),
        Field('style', default='V', length=1, label='Game style'),
        Field('cabinet', 'reference cabinets', required=True),
        Field('seal_num', 'integer', label='Seal number'),
        Field('multi_denom', 'boolean', required=True, default=False, label='Multidenom', represent=lambda v,r: 'Y' if v else 'N'),
        Field('multi_game', 'boolean', required=True, default=False, label='Multigame', represent=lambda v,r: 'Y' if v else 'N'),
        Field('bv_model', label='BV model', default=''),
        Field('bv_firmware', label='BV firmware', default=''),
        Field('printer_model', label='Printer model', default=''),
        Field('printer_firmware', label='Printer firmware', default=''),
        Field('board_level', label='Board level', default=''),
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
    db.define_table('finals',
        Field('final_date', 'date', default=datetime.today(), required=True),
        Field('machine', 'reference all_machines', required=True),
    )
    db.define_table('installs',
        Field('install_date', 'date', default=datetime.today(), required=True),
        Field('machine', 'reference all_machines', required=True),
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
        Field('machine', 'reference cabinets', required=True),
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
        data_dir = 'U:\\floor_data'
    col.init()
    bart = PoorBart()
    bart.data_dir = data_dir
    bart.cmdloop()

