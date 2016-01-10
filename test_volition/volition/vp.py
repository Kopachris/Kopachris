# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

## VP module
## Copyright (c) 2012 by Christopher Koch

"""This module contains classes and methods for handling "Volition Package" (VP) files."""

## No guarantees about pep8 compliance

import time
import logging
from bintools import *
from . import VolitionError, FileFormatError

# logging.basicConfig(filename="vp.log", level=logging.DEBUG)

class FileNotFoundError(VolitionError):
    def __init__(self, path, msg):
        self.path = path
        self.msg = msg
        
    def __str__(self):
        return "File not found: {}, {}.".format(self.path, self.msg)
        
class VolitionPackageError(VolitionError):
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg

class VolitionPackageFile:
    """A VP directory tree.  Folders are stored as Folder objects and files are stored as File objects containing
    the contents of the file.  The constructor takes a file-like object as a required argument and creates the
    necessary File and Folder objects to fill the directory tree, self.vp_file_directory.  Internally, all folders
    and files are stored in a Folder object with the name attribute "root."  However, all read and write methods
    are written to take paths starting with the first entry in the actual VP file's index (usually "data")."""
    def __init__(self, vp_file):
        logging.info("Creating a VolitionPackageFile object.")
        vp_file_id = vp_file.read(4)
        logging.debug("File ID {}".format(vp_file_id))
        if vp_file_id != b"VPVP":
            raise FileFormatError(vp_file, "Not a VP file.")
            
        vp_file_version = unpack_int(vp_file.read(4))
        logging.debug("File spec version {}".format(vp_file_version))
        if vp_file_version > 2:
            raise FileFormatError(vp_file, "VP spec version greater than 2.")
            
        vp_diroffset = unpack_int(vp_file.read(4))
        logging.debug("diroffset {}".format(vp_diroffset))
        vp_num_files = unpack_int(vp_file.read(4))
        logging.info("VP contains {} dir entries".format(vp_num_files))
        
        vp_file_directory = Folder(b"root")
        parent_directory = vp_file_directory
        
        vp_file.seek(vp_diroffset)
        
        logging.info("Reading VP file")
        for i in range(vp_num_files):
            this_file_offset = unpack_int(vp_file.read(4))
            this_file_size = unpack_int(vp_file.read(4))
            this_file_name_long = vp_file.read(32)
            this_file_name = this_file_name_long.rstrip(b'\0')
            this_file_timestamp = unpack_int(vp_file.read(4))
            vp_dir_location = vp_file.tell()
            
            if not this_file_offset or not this_file_size or not this_file_timestamp:
                # direntry is either folder or backdir
                
                if this_file_name != b"..":     # folder
                    logging.debug("Folder {}".format(this_file_name))
                    this_node = Folder(this_file_name, parent_directory)
                    parent_directory.contents.add(this_node)
                    parent_directory = this_node
                else:                           # backdir
                    logging.debug("Backdir")
                    this_node = parent_directory
                    parent_directory = this_node.parent
            else:
                # direntry is a file
                
                logging.debug("File {}".format(this_file_name))
                vp_file.seek(this_file_offset)
                this_file_data = vp_file.read(this_file_size)
                this_node = File(this_file_name, this_file_data, this_file_timestamp, parent_directory)
                parent_directory.contents.add(this_node)
                vp_file.seek(vp_dir_location)
                
        logging.debug("Last file {}".format(this_node))
                
        self.vp_file_directory = vp_file_directory
        
    def get_file(self, path, sep='/'):
        """Returns a File object or Folder object for further processing.  Takes a full path including the file/folder name
        as a required argument and a separator character as an optional argument."""
        parent_directory = self.vp_file_directory
        split_path = path.split(sep)
        logging.info("Retrieving file {}".format(path))
        logging.debug("Split path is {}".format(split_path))
        cur_node = parent_directory.contents
        logging.debug("cur_node at begin is {}".format(cur_node))
        
        # traverse path
        for i, cur_dir in enumerate(split_path):
            for dir in cur_node:
                if dir.name == cur_dir:
                    logging.debug("Found match. Current dir is {}".format(dir))
                    parent_directory = dir
                    cur_node = dir.contents
                    break
            else:
                raise FileNotFoundError(path, "{} does not exist".format(cur_dir))
                
        # At this point, dir or parent_directory matches the
        # last item in split_path and cur_node is the contents
        # of that item, whether it's a file or folder.
        # parent_directory is a File object or Folder object
        # cur_node is a set of File objects and/or Folder objects
                    
        return parent_directory
        
    def remove_file(self, path, sep='/'):
        """Removes a file or folder from the directory.  Takes a full path including the file/folder name
        as a required argument and a separator character as an optional argument."""
        parent_directory = self.vp_file_directory
        split_path = path.split(sep)
        logging.info("Removing file {}".format(path))
        logging.debug("Split path is {}".format(split_path))
        cur_node = parent_directory.contents
        logging.debug("cur_node at begin is {}".format(cur_node))
        path_depth = len(split_path) - 1
        
        # traverse path
        for i, cur_dir in enumerate(split_path):
            for dir in cur_node:
                if dir.name == split_path[i]:
                    logging.debug("Found match. cur_node is {}".format(dir))
                    parents_parent = parent_directory
                    parent_directory = dir
                    cur_node = dir.contents
                    break
            else:
                raise FileNotFoundError(path, "{} does not exist".format(cur_dir))
                    
        # At this point, dir or parent_directory matches the
        # last item in split_path and cur_node is the contents
        # of that item, whether it's a file or folder.
        # parent_directory is a File object or Folder object
        # cur_node is a set of File objects and/or Folder objects
                    
        if parent_directory.name == split_path[path_depth]:
            parents_parent.contents.remove(parent_directory)
        else:
            raise FileNotFoundError(path, " does not exist")
        
    def add_file(self, path, file, sep='/'):
        parent_directory = self.vp_file_directory
        split_path = path.split(sep)
        logging.info("Adding file {} to {}".format(file.name, path))
        
        cur_node = parent_directory.contents
        
        path_depth = len(split_path)
        
        for i, cur_dir in enumerate(split_path):
            for dir in cur_node:
                if dir.name == cur_dir:
                    logging.debug("Found match. cur_node is {}".format(dir))
                    parent_directory = dir
                    cur_node = dir.contents
                    break
            else:
                raise FileNotFoundError(path, "{} does not exist".format(cur_dir))
                
        # At this point, dir or parent_directory matches the
        # last item in split_path and cur_node is the contents
        # of that item, whether it's a file or folder.
        # parent_directory is a File object or Folder object
        # cur_node is a set of File objects and/or Folder objects
        
        cur_node.add(file)
        
    def make_vp_file(self):
        logging.info("Making binary VP file...")
        self.cur_index = list()
        self.cur_files = list()
        self.cur_offset = 16        # header size == beginning offset is always 16 bytes
        self._recurse_thru_directory(self.vp_file_directory.contents)
        
        vp_dir_offset = self.cur_offset
        vp_num_files = len(self.cur_index)
        
        vp_header = b"".join([b"VPVP",
                             pack_int(2),
                             pack_int(vp_dir_offset),
                             pack_int(vp_num_files)])
        vp_files = b"".join(self.cur_files)
        vp_index = b"".join(self.cur_index)
        
        logging.info("Success!")
        logging.debug("VP directory offset {}".format(vp_dir_offset))
        logging.debug("Number of VP directory entries {}".format(vp_num_files))
        
        return b"".join([vp_header, vp_files, vp_index])
        
    def _recurse_thru_directory(self, vp_file_directory):
        # vp_file_directory should be a set - the contents of a Folder
        cur_index = self.cur_index
        cur_files = self.cur_files
        cur_offset = self.cur_offset
            
        # This function should recurse through vp_file_directory, not returning anything,
        # but updating self.cur_index, etc. at the end of each branch
            
        for cur_node in vp_file_directory:
            if isinstance(cur_node, Folder):
                this_entry_offset = 0
                this_entry_size = 0
                this_entry_name = cur_node.name.encode()
                this_entry_timestamp = 0
                
                # add index entry for folder:
                cur_index.append(b"".join([pack_int(this_entry_offset),
                                          pack_int(this_entry_size),
                                          this_entry_name.ljust(32, b'\0'),
                                          pack_int(this_entry_timestamp)]))
                                          
                # save current state:
                self.cur_index = cur_index
                self.cur_files = cur_files
                self.cur_offset = cur_offset
                
                self._recurse_thru_directory(cur_node.contents)
                
                # load current state:
                cur_index = self.cur_index
                cur_files = self.cur_files
                cur_offset = self.cur_offset
            elif isinstance(cur_node, File):
                this_entry_offset = cur_offset
                this_entry_size = len(cur_node)
                this_entry_name = cur_node.name.encode()
                this_entry_timestamp = cur_node.timestamp
                
                cur_offset += this_entry_size
                cur_files.append(cur_node.contents)
                
                # add index entry for file:
                cur_index.append(b"".join([pack_int(this_entry_offset),
                                          pack_int(this_entry_size),
                                          this_entry_name.ljust(32, b'\0'),
                                          pack_int(this_entry_timestamp)]))
            else:
                raise VolitionPackageError("{} is {}, expected File or Folder".format(cur_node, type(cur_node)))
                
        # add backdir
        this_entry_offset = 0
        this_entry_size = 0
        this_entry_name = b".."
        this_entry_timestamp = 0
        
        # add index entry:
        cur_index.append(b"".join([pack_int(this_entry_offset),
                                  pack_int(this_entry_size),
                                  this_entry_name.ljust(32, b'\0'),
                                  pack_int(this_entry_timestamp)]))
                                  
        # save current state:
        self.cur_index = cur_index
        self.cur_files = cur_files
        self.cur_offset = cur_offset
        
class Folder:
    def __init__(self, name, parent="", contents=None):
        self.name = name.decode().lower()
        if contents is not None:
            self.contents = set(contents)
        else:
            self.contents = set()
        self.parent = parent
        self.parent_name = str(parent)
        
    def __eq__(self, other):
        if self.name == other.name and self.parent == other.parent:
            return True
        else:
            return False
            
    def __hash__(self):
        return hash(self.name)
        
    def __repr__(self):
        return "/".join([self.parent_name, self.name])
        
class File:
    def __init__(self, name, contents, timestamp=False, parent=""):
        self.name = name.decode().lower()
        self.contents = contents
        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = int(time.clock())
        self.parent = parent
        self.parent_name = str(parent)
            
    def __len__(self):
        return len(self.contents)
        
    def __eq__(self, other):
        if self.name == other.name and self.parent == other.parent:
            return True
        else:
            return False
            
    def __hash__(self):
        return hash(self.name)
        
    def __repr__(self):
        return "/".join([self.parent_name, self.name])