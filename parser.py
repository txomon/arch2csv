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

import xml.dom.minidom as minidom
import subprocess

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
			# If this is an empty string (was emptyline) go to next iteration
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
				# I found that the arch currently is has a bug because outputs this:
				# capture_stats.stats_iface eth2: 
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

	def get_attributes(self):
		""" () -> dict(str: list of str)
		It returns the dict contaning attributes as keys and parsed values as lists
		"""
		return self.dictionary.copy()

class Operations:
	
	def _make_identifier(receive):
		bad_strings = ".:-"
		good_strings = "_"*len(bad_strings)
		table=str.maketrans(bad_strings,good_strings)
		if receive == "-":
			return receive
		return receive.translate(table)
		
	def _operations_list_to_string(operations):
		""" (list | str) -> str
		The function returns a plain string of the inner lists
		
		>>> _operations_list_to_string(['a','+',[['b','+','d'],'*','c']])
		'(a+((b+d)*c))'
		"""
		if type(operations) == list:
			result = '('
			for operation in operations:
					result += Operations._operations_list_to_string(operation)
			return result + ')'
		elif type(operations) == str:
			return Operations._make_identifier(operations)

	def operations_to_result(parameter_definition, dictionary_of_values):
		""" (dict, dict) -> dict
		Returns the result of doing the operations for each value in parameter_definition
		with the values in dictionary_of_values in each index in a dictionary indexed
		by the keys of parameter_definition.
		
		>>> operations_to_result({"parameterA": ["a","+","b","+","c"],"parameterB": ["a", "*", "c"]},{"a": [3,2,3,4],"b": [2,1,3,4],"c": [1,3,5,2]})
		{"parameterA": [6,6,11,10], 
			"parameterB": [3,6,15,8]}
		"""
		result = dict()
		var_list = dict()
		count = 0
		for index in values:
			if len(values[index]) > count:
				count = len(values[index])
		for index in range(count):
			if index == 0:
				for parameter in parameter_definition:
					result[parameter]=list()
			for operand in dictionary_of_values:
				identifier_operand = Operations._make_identifier(operand)
				try:
					var_list[identifier_operand] = float(dictionary_of_values[operand][index])
				except: continue

			for parameter in parameter_definition:
				operations_string = Operations._operations_list_to_string(parameter_definition[parameter])
				result[parameter].append(eval(operations_string, None, var_list))
		return result

class OutFile:
	"""
	It is the output file that has all the selected attributes with their
	values
	"""
	def __init__(self, outfile):
		"""
		Receives the name of the output file it will use
		"""
		self.outfile = outfile

	def columns_output(self, attributes, sep=" "):
		"""
		Prints the attributes with its values in the file in columns
		"""
		count = 0
		for index in attributes:
			if len(attributes[index]) > count:
				count = len(attributes[index])
		for parameter in attributes:
			print(parameter, file=self.outfile, end=sep)
		print("\n", file=self.outfile, end="")
		for index in range(count):
			for parameter in attributes:
				print('{0:.15f}'.format(float(attributes[parameter][index])), file=self.outfile, end=sep)
			print("\n", file=self.outfile, end="")
		self.outfile.close()

class GraphicFile:
	"""
	It is meant to be a Graphics file that represents the data
	"""
	pass


class XMLFile:
	"""
	It is the xml input file that is meant to describe what 
	the program has to do.
	
	To be able to be checked against the following dtd
	and the xml file should be something like bellow's:
	<!DOCTYPE conf [
	<!ELEMENT conf (parameters?,graphs?)>
	<!ELEMENT parameters (parameter+)>
	<!ELEMENT parameter (#PCDATA|operation)*>
	<!ATTLIST parameter name ID #REQUIRED>
	<!ATTLIST parameter row CDATA #IMPLIED>
	<!ELEMENT operation ((operand1?,operand2?)|operand*)>
	<!ATTLIST operation name CDATA #IMPLIED>
	<!ATTLIST operation operator CDATA #REQUIRED>
	<!ATTLIST operation operand1 CDATA #IMPLIED>
	<!ATTLIST operation operand2 CDATA #IMPLIED>
	<!ELEMENT operand1 (operation)>
	<!ELEMENT operand2 (operation)>
	<!ELEMENT operand (operation?)>
	<!ATTLIST operand row CDATA #IMPLIED>
	<!ELEMENT graphs (graph+)>
	<!ELEMENT graph (xaxys?,yaxys?)>
	<!ATTLIST graph name ID #REQUIRED>
	<!ATTLIST graph xaxys IDREF #IMPLIED>
	<!ATTLIST graph yaxys IDREF #IMPLIED>
	<!ELEMENT xaxys (operation)>
	<!ELEMENT yaxys (operation)>
	]>
	
	<conf> <!-- Root tag -->
		<parameters> <!-- The parameters we want to output -->
			<parameter name="dag.total_time" row="total_time"/><!-- The output parameter name is not same as the row name -->
			<parameter name="softirq_persec">
				<operation operator="/"
					operand1="capture_stats.soft_interrupt_cycles"
					operand2="dag.total_time" 
					/> <!-- If we don't want to have a parameter in the output, we just use it's row -->
			</parameter>
			<parameter name="dag.packets_per_second"/>
		</parameters>
		<!-- Not supported yet -->
		<graphs> <!-- The graphs we want to generate -->
			<graph name="filename" xaxys="dag.packets_per_second"> <!-- One graph with its file name -->
				<yaxys> <!-- columns to be in the y axis -->
					<operation operator="+"
						operand1="capture_stats.soft_interrupt_cycles">
						<operand2>
							<operation operator="*"
								operand="dag.total_time"
								operand="1000"
							/>
						</operand2>
					</operation>
				</yaxys>
			</graph>
		</graphs>
		<!-- Not supported yet -->
	</conf>
	"""

	def __init__(self, xml_file):
		"""
		Receives the xml_file and makes a sanitycheck on the xml file
		"""

		self.rows = list()
		self.parameters = dict()
		self.named_operations = dict()
		# We first parse the xml file
		self.dom = minidom.parse(xml_file)

		# We check if the xml syntax fits into the dtd
		self._check_xml_syntax(xml_file.name)
		
		# Now that we know its alright, we check all the structure
		# searching for something missing, and create the internal structure
		self._check_xml()
		xml_file.close()

	def get_parameters(self):
		return self.parameters.copy()

	def get_rows(self):
		return list(self.rows)

	def _check_xml_syntax(self,xml_file_name):
		"""
		Writes the dtd in /tmp/parser.dtd and checks received xml against it,
		exiting from the program if check fails
		"""

		dtd = self.__doc__.partition("<!DOCTYPE conf [")[2].partition("]>")[0].expandtabs(0)

		# Open the file in overwrite mode in a tmpfs
		dtd_file = open("/tmp/parser.dtd","w")

		# We write the dtd content
		dtd_file.write(dtd)

		# And we close it
		dtd_file.close()

		# We call xmllint to check against the dtd
		if 0 != subprocess.call(["xmllint", "--noout", "--dtdvalid", "/tmp/parser.dtd",xml_file_name]):
			# If it failed, we will suppose that the xml didn't pass the check
			print("Use /tmp/parser.dtd to check your xml's syntax with:")
			print("\txmllint --noout --dtdvalid /tmp/parser.dtd xmlfile")
			# And we exit
			exit()

	def _check_xml(self):
		# We first check that we just have one child node
		self.__delete_empty_textnodes(self.dom)
		
		if len(self.dom.childNodes) != 1:
			raise minidom.xml.dom.HierarchyRequestErr("Can't find just one root tag")
		self.__check_xml_conf(self.dom.childNodes[0])

	def __check_xml_conf(self,node):
		if node.nodeType != minidom.Node.ELEMENT_NODE:
			raise minidom.xml.dom.HierarchyRequestErr("The root node is not an element node")
		if node.nodeName != 'conf':
			raise minidom.xml.dom.HierarchyRequestErr("The root node is not a <conf> node")
		if not node.hasChildNodes():
			raise minidom.xml.dom.HierarchyRequestErr("The conf node is empty")
		if len(node.childNodes) > 2:
			raise minidom.xml.dom.HierarchyRequestErr("There are too many childs in conf node")
		for child in node.childNodes:
			if child.nodeType != minidom.Node.ELEMENT_NODE:
				raise minidom.xml.dom.HierarchyRequestErr("conf's child node wasn't an element node:",child)
			elif child.nodeName == 'parameters':
				self.__check_xml_parameters(child)
			elif child.nodeName == 'graphs':
				pass #not supported yet

	def __check_xml_parameters(self,parameters):
		if not parameters.hasChildNodes():
			raise minidom.xml.dom.HierarchyRequestErr("There <parameters> node has no childs")
		for parameter in parameters.childNodes:
			if parameter.nodeType != minidom.Node.ELEMENT_NODE:
				raise minidom.xml.dom.HierarchyRequestErr("<parameters>'s child node isn't an element node (<parameter>): "+child.__str__())
			if parameter.nodeName != 'parameter':
				raise minidom.xml.dom.HierarchyRequestErr("A <parameters>'s child node is not a <parameter> node")
			if not parameter.hasAttributes():
				raise minidom.xml.dom.HierarchyRequestErr("The <parameter> node doesn't have any attribute (name attribute is required)")
			if not parameter.hasAttribute('name'):
				raise minidom.xml.dom.HierarchyRequestErr("The parameter node doesn't have name attribute")
			if parameter.hasChildNodes() and parameter.hasAttribute('row'):
				raise minidom.xml.dom.HierarchyRequestErr("The parameter node has too many source definition (row attribute and childs defined)")
			if parameter.hasAttribute('row'):
				self.__add_row_to_internal(parameter.getAttribute('name'),[parameter.getAttribute('row')])
			elif parameter.hasChildNodes():
				if len(parameter.childNodes) != 1:
					raise minidom.xml.dom.HierarchyRequestErr("The parameter node must have just 1 <operation> child or a row attribute")
				else:
					rows = self.__check_xml_operators(parameter.childNodes[0])
					self.__add_row_to_internal(parameter.getAttribute('name'),rows)
			else:
				self.__add_row_to_internal(parameter.getAttribute('name'),[parameter.getAttribute('name')])

	def __check_xml_operators(self,operation):
		if operation.nodeName != 'operation':
			raise minidom.xml.dom.HierarchyRequestErr("There must be just 1 node <operation>")
		if not operation.hasAttribute('operator'):
			raise minidom.xml.dom.HierarchyRequestErr("operator attribute is needed")
		operator = operation.getAttribute('operator')
		result = list()
		if operator in '/-':
			if operation.hasAttribute('operand'):
				raise minidom.xml.dom.HierarchyRequestErr("operators '/' and '-' don't support operand element")
			if operation.hasAttribute('operand1'):
				operand1 = operation.getAttribute('operand1')
				if operand1 in self.named_operations.keys():
					operand1 = self.named_operations[operand1]
			if operation.hasAttribute('operand2'):
				operand2 = operation.getAttribute('operand2')
				if operand2 in self.named_operations.keys():
					operand2 = self.named_operations[operand2]
					
			for operand in operation.childNodes:
				if operand.nodeName == 'operand1':
					try:
						operand1
					except NameError:
						operand1 = self.__check_xml_operators(operand.childNodes[0])
					else:
						raise minidom.xml.dom.HierarchyRequestErr("operand1 is already defined, xml syntax error")
				elif operand.nodeName == 'operand2':
					try:
						operand2
					except NameError:
						operand2 = self.__check_xml_operators(operand.childNodes[0])
					else:
						raise minidom.xml.dom.HierarchyRequestErr("operand2 is already defined, xml syntax error")
				else:
					raise minidom.xml.dom.HierarchyRequestErr(operand.nodeName, "is not expected to be in '/' or '-' operation node")
			try:
				operand1
				operand2
			except NameError:
				raise minidom.xml.dom.HierarchyRequestErr("Some operand is not defined, check for operand1 and operand2")
			result = [operand1, operator, operand2]
		elif operator in '+*':
			if operation.hasAttribute('operand1') or operation.hasAttribute('operand2'):
				raise minidom.xml.dom.HierarchyRequestErr("operators '/' and '-' don't support operand element")
			if not operation.hasChildNodes():
				raise minidom.xml.dom.HierarchyRequestErr("<operand> nodes are needed for this type of operation")
			for operand in operation.childNodes:
				if operand.nodeName != 'operand':
					raise minidom.xml.dom.HierarchyRequestErr(operand.nodeName, "is not expected to be in '*' or '+' operation node")
				if operand.hasAttribute('row'):
					row_name = operand.getAttribute('row')
					if  row_name in self.named_operations.keys():
						result.extend([self.named_operations[row_name], operator])
					else:
						result.extend([operand.getAttribute('row'), operator])
				else:
					result.extend([self.__check_xml_operators(operand.childNodes[0]),operator])
			result.pop()
		if operation.hasAttribute('name'):
			self.named_operations[operation.getAttribute('name')] = result
		return result

	def __add_row_to_internal(self,name,rows):
		if not (type(name) == str and type(rows) == list):
			raise TypeError("Wrong argument types")
		if ' ' in name:
			raise minidom.xml.dom.HierarchyRequestErr("The name '"+name+"' is not valid because can't contain spaces")
		for row in self.__operation_list_to_row_list(rows):
			if ' ' in row:
				raise minidom.xml.dom.HierarchyRequestErr("The row '"+row+"' is not valid because can't contain spaces")
			try:
				float(row)
			except ValueError:
				if not row in self.rows:
					self.rows.append(row)
		if not name in self.parameters.keys():
			self.parameters[name] = rows
		else:
			for row in rows:
				if not row in self.parameters[name]:
					raise minidom.xml.dom.HierarchyRequestErr("The name '"+name+"' has different "
					"data definitions\n("+rows.__str__()+")\n VS \n("+self.parameters[name].__str__()+")")

	def __operation_list_to_row_list(self,operation_list):
		result = list()
		if len(operation_list) == 1:
			return operation_list
		for index in range(0,len(operation_list),2):
			if type(operation_list[index]) == list:
				result.extend(self.__operation_list_to_row_list(operation_list[index]))
			elif type(operation_list[index]) == str:
				result.append(operation_list[index])
		return result

	def __delete_empty_textnodes(self,parent):
		for child in tuple(parent.childNodes):
			if child.hasChildNodes():
				self.__delete_empty_textnodes(child)
			elif (child.nodeType in [	minidom.Node.CDATA_SECTION_NODE,
							minidom.Node.COMMENT_NODE,
							minidom.Node.TEXT_NODE]
				):
				if child.data.strip() == '' or child.nodeType == minidom.Node.COMMENT_NODE:
					parent.removeChild(child)

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
	xmlfile = XMLFile(arguments.xml_config[0])
	logfiles={}
	rows_values = {}
	for log_file_descriptor in arguments.log_file:
		logfile = LogFile(log_file_descriptor)
		values = logfile.get_attributes()
		parameters = xmlfile.get_parameters()
		rows = xmlfile.get_rows()
		for log_row in dict(values):
			if log_row in rows:
				continue
			for row in rows:
				if row != log_row and row in log_row: values[row]=values[log_row]
		result = Operations.operations_to_result(parameters, values)
		out_file = OutFile(open(log_file_descriptor.name + ".parameters", mode="w"))
		out_file.columns_output(result)

