import cmd
import sys

from dateutil.parser import parse as parse_date
import pydal
from pydal import DAL, Field


class GradesShell(cmd.Cmd):
    intro = "Welcome to grading database command line.\nType help or ? to list commands."
    prompt = '(local) ?? '
    
    def do_quit(self, args):
        """Exit the program."""
        sys.exit(0)
        
    def do_exit(self, args):
        """Exit the program."""
        sys.exit(0)
    
    def do_add_student(self, args):
        """Add a new student record to the database."""
        fname = input("First name? ")
        lname = input("Last name? ")
        dob = parse_date(input("Date of birth? "))
        sex = input("Sex? ")
        if sex.lower().startswith('m'):
            sex_is_f = False
        elif sex.lower().startswith('f'):
            sex_is_f = True
        else:
            print("Sex must be (m)ale or (f)emale.\n\nRecord not added.")
            return False
            
        record = self.db.students.insert(fname=fname, lname=lname, dob=dob, sex_is_f=sex_is_f)
        self.db.commit()
        
        print("Added student: " + str(self.db.students[record]))
    
    def preloop(self):
        db = DAL('sqlite://grades.db')
        db.define_table('students',
                        Field('fname', notnull=True),
                        Field('lname', notnull=True),
                        Field('dob', 'date', notnull=True),
                        Field('sex_is_f', 'boolean', notnull=True),
                        )
        db.define_table('courses',
                        Field('course_id', notnull=True),
                        Field('category', notnull=True),
                        Field('description', notnull=True),
                        Field('professor', notnull=True),
                        Field('classroom', notnull=True),
                        Field('long_descr', 'text'),
                        Field('start_date', 'date', notnull=True),
                        Field('end_date', 'date', notnull=True),
                        )
        db.define_table('students_to_courses',
                        Field('student', 'reference students', notnull=True),
                        Field('course', 'reference courses', notnull=True),
                        )
        db.define_table('assignments',
                        Field('course', 'reference courses', notnull=True),
                        Field('description', notnull=True),
                        Field('max_points', 'integer', notnull=True),
                        Field('due_date', 'date', notnull=True),
                        )
        db.define_table('grades',
                        Field('student', 'reference students', notnull=True),
                        Field('assignment', 'reference assignments', notnull=True),
                        Field('grade', 'integer'),
                        )
        self.db = db


if __name__ == '__main__':
    GradesShell().cmdloop()