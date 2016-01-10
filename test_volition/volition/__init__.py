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

## volition package
## Copyright (c) 2012 by Christopher Koch

"""This package contains a set of modules for handling file types used by the game FreeSpace 2, originally developed by Volition, Inc."""

__all__ = ["pof", "vp"]

## __all__ should include:
# pof
# vp
# vf
# ani
# tbl
# pcx
## but not:
# bintools

class VolitionError(Exception):
    """Base class for exceptions in this module."""
    pass

class FileFormatError(VolitionError):
    """Exception raised for invalid filetype errors.

    Attributes:
        path -- the filepath of the invalid file
        msg  -- a message"""
    def __init__(self, path, msg):
        self.path = path
        self.msg = msg
        
    def __str__(self):
        return "{}, {}.".format(self.msg, self.path)