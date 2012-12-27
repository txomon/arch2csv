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

import xml.etree.ElementTree as ET

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
		
		# We initialize the object to 0
		self.dictionary = {}
		self.test_number = 0
		
		# Read each line of the file
		for line in logfile:
			# Erase spaces and newline chars
			line = line.rstrip("\n")
			# If this is an empty string (was newline) go to next iteration
			if not line: continue
			# If this line is a comment
			if line[0] == "#":
				# We increase the test we are in
				self.test_number += 1
			# By design constraints, the rest are attributes and values
			else:
				# We create a tuple from the line, separing attribute and value
				temp = line.partition(sep)
				# We check that temp[1] exits, if it doesn't, this is not a real logfile
				#+I found that the arch currently is has a bug because outputs this:
				#+capture_stats.stats_iface eth2: 
				if temp[1] == "":
					# We split it from the space
					temp = line.rpartition(" ")
					# If we can't split by the colon and get sure it gets partitioned,
					# it is not a real logfile
					if (temp[2].rpartition(":")[1] != ":" or temp[2].rpartition(":")[2] != ""):
						raise ValueError("The provided file", logfile, "is not a real logfile")
					# We reconstruct temp tuple if it passed the sanitycheck
					temp = (temp[0], ": ", temp[2].rpartition(":")[1])
				# If the attribute is already in the dictionary
				if temp[0] in self.dictionary:
					# If we have a value
					if temp[2]:
						# Add the value to the list of the dictionary's value
						self.dictionary[temp[0]].insert(self.test_number, temp[2])
					# if we don't have a value
					else:
						# Add a 0 to the list of the dictionary
						self.dictionary[temp[0]].insert(self.test_number, 0)
				# If the attribute is not in the dictionary
				else:
					# If we have a value to put
					if temp[2]:
						# We create a key-list dictionary entry 
						# with the attribute and the value
						self.dictionary[temp[0]]=[temp[2]]
					# if we don't have anything
					else:
						# We create a 0 value in the entry
						self.dictionary[temp[0]]=[0]

	def get_values(self, attribute):
		""" (str) -> list of str
		It returns a list of the values of the attribute in 
		the file
		"""
		return self.dictionary[attribute]

	def get_attributes(self):
		""" () -> list of str
		It returns the list of attributes in the log file
		"""
		return self.dictionary.keys()


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
	the program has to do.
	
	The xml file should have the following structure:
	<conf> <!-- Root tag --!>
		<parameters> <!-- The parameters we want to output --!>
			<parameter name="dag.total_time" alias="total_time"/><!-- One of the parameters we want to output --!>
			<parameter alias="softirq_persec">
				<operation operator="/"
					operand1="capture_stats.soft_interrupt_cycles"
					operand2="dag.total_time" 
				/>
			</parameter>
		</parameters>
		<graphs> <!-- The graphs we want to generate --!>
			<graph name="filename"> <!-- One graph with its file name --!>
				<xaxys> <!-- columns to be in the x axis, this could also be in the graph node as an attribute --!>
					dag.packets_per_second
				</xaxys>
				<yaxys> <!-- columns to be in the y axis --!>
					<operation operator="+"
						operand1="capture_stats.soft_interrupt_cycles">
						<operand2>
							<operation operator="*"
								operand1="dag.total_time"
								operand2="1"
							/>
						</operand2>
					</operation>
				</yaxys>
			</graph>
		</graphs>
	</conf>
	"""
	def __init__(self, xml_file):
		"""
		Receives the xml_file and parses it, creating its internal
		data structure
		"""
		self.tree = ET.parse(xml_file)

	def get_attributes(self):
		return self.tree.findall("./conf/parameters

# If this script is used as an script
if __name__ == "__main__":

	###
	## We first start parsing arguments
	import argparse
	
	# First, we describe the program
	arg_parser = argparse.ArgumentParser(
		description = "A script that parses log files and outputs them as csv files",
		epilog = "Bugs should be sent to javierdo1<at>gmail<dot>com",
		)

	# Then we start adding the arguments it supports

	# The xml config file is totally needed, it is the first argument to be put
	arg_parser.add_argument("xml_config", nargs = 1,
				type = argparse.FileType("r"),
				help = "The XML config file you want to use")

	# The log files to be parsed should be passed
	arg_parser.add_argument("log_file", nargs = "+",
				type = argparse.FileType("r"),
				help = "The log file to be parsed")

	arguments = arg_parser.parse_args()
	## Ends argument parsing
	###
	
	###
	## Start initializing the LogFile classes
	logfiles={}
	for log_file in arguments.log_file:
		logfiles[log_file.name] = LogFile(log_file)

	xmlfile = XMLFile(arg_parser.xml_config)