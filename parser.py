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
	It represents a log file, with all the rows accessible in 
	the right order
	"""

	
	def __init__(self, logfile, sep=": "):
		""" (file[, sep=": "])
		Receives the logfile it has to parse and extract the information
		from using sep as the separator between attribute and value
		"""
		self.dictionary = {}
		self.test_number = 0
		for line in logfile:
			line = line.strip()
			continue if not line
			if line[0] == "#":
				self.test_number += 1
			else:
				
			

	def get_values(self, attribute):
		""" (str) -> list of str
		It returns a list of the values of the attribute in 
		the file
		"""

	def get_attributes(self):
		""" () -> list of str
		It returns the list of attributes in the log file
		"""


class OutFile:
	"""
	It is the output file that has all the selected attributes with their
values
	"""
	def __init__(self, outfile):
		"""
		Receives the name of the output file it will use
		"""

	def write_attributes(self, attributes):
		"""
		Prints the attributes with its values in the file
		"""

class GraphicFile:
	"""
	It is meant to be a Graphics file that represents the data
	"""
	pass


class XMLFile:
	"""
	It is the xml input file that is meant to describe what 
	the program has to do
	"""
	def __init__(self, xml_file):
		"""
		Receives the xml_file and parses it, creating its internal
		data structure
		"""

# If this script is used as an script
if __name__ == "__main__":

	###
	## We first start parsing arguments
	import argparse
	
	# First, we describe the program
	arg_parser = argparse.ArgumentParser(
		description="A script that parses log files and outputs them as csv files",
		epilog="Bugs should be sent to javierdo1<at>gmail<dot>com",
		)

	# Then we start adding the arguments it supports

	# The xml config file is totally needed, it is the first argument to be put
	arg_parser.add_argument("xml_config", nargs=1,
				type=argparse.FileType("r"),
				help="The XML config file you want to use")

	# The log files to be parsed should be passed
	arg_parser.add_argument("log_file", nargs="+", action="append",
				type=argparse.FileType("r"),
				help="The log file to be parsed")

	arguments = arg_parser.parse_args()
	## Ends argument parsing
	###
	
	###
	## Start initializing the LogFile classes
	for log_file in arguments.log_file:
		logfile = LogFile(log_file)
		