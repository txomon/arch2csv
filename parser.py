#!/usr/bin/env python
# Copyright (C) 2012 Javier Domingo

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

class LogFile:
	"""
	It is a log file, with all the rows accessible in the right order
	"""

	def __init__(self, logfilename):
		"""
		Receives the file name it has to parse and extract the attributes from
		"""

	def get_values(self, attribute):
		"""
		It returns a list of the values of the attribute in the file
		"""

	def get_attributes(self):
		"""
		It return a list of the attributes in the log file
		"""


class OutFile:
	"""
	It is the output file that has all the selected attributes with their values
	"""
	def __init__(self, outfilename):
		"""
		Receives the name of the output file it will use
		"""

	def print(self, attributes, values):
		"""
		Prints the attributes with its values in the file
		"""

class Parser:
