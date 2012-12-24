#!/usr/bin/env python2.5
# Copyright (C) 2008 by Jon de Andres

# Variables of the interpreter (arguments i.e.)
import sys
# Interfaces with the OS
import os
# Subprocess with accesible streams
import popen2
# Common string operations
import string
# Hierarquical data structures convertible from/to xml
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

# Class to contain all the structure of a operator/column
class Operator:

    def __init__(self):
        self.type = ''
        self.name = ''
        self.value = 0

        self.operation = 0

class Operation:

    def __init__(self, operation, *args):
        self.op_types = {'+': self.add, '-': self.sub, '*': self.mul, '/': self.div, 'none': self.data}

        self.op_value = operation
        self.op = self.op_types[self.op_value]

        self.operators = []
        self.variables = []

    def add(self, oper1, oper2):
        """
        Add two operands
        """
        return oper1 + oper2

    def sub(self, oper1, oper2):
        """
        Substract two operands
        """

        return oper1 - oper2

    def mul(self, oper1, oper2):
        """
        Multiply two operands
        """

        return oper1 * oper2

    def div(self, oper1, oper2):
        """
        Divide two operandsi
        """

#        print oper1
#        print oper2

        return oper1 / oper2

    def data(self):
        operator = self.operators[0]
        return operator.value

TABLEGEN = "tablegen"

class Parser:

    def __init__(self, f_results, f_conf):

        self.results = f_results
        self.conf = f_conf
        self.data = []
        self.operations = []
        self.variables = []
        self.headers = []

    def set_operations(self):
        conf = ET.parse(self.conf)
        rows = conf.findall("row")

        for row in rows:
            op_node = row.find("op")

            try:
                op_type = op_node.attrib["type"]

                op = Operation(op_type)
                self.operations.append(op)

                operators = op_node.findall("oper")
                for operator_node in operators:
                    operator = Operator()
                    operator.type = operator_node.attrib["type"]

                    if operator.type ==  "variable":
                        operator.name = operator_node.text
                        operator.operation = 0
                        if operator.name not in self.variables:
                            self.variables.append(operator.name)
                        if operator.name not in op.variables:
                            op.variables.append(operator.name)

                    elif operator.type == "complex":
#                        print operator.type
                        subop_node = operator_node.find("op")
                        subop_type = subop_node.attrib["type"]
#                        print subop_type
                        subop = Operation(subop_type)
                        operator.operation = subop

                        #same job again...
                        sub_operators = subop_node.findall("oper")

                        for sub_operator_node in sub_operators:
                            sub_operator = Operator()
                            sub_operator.type = sub_operator_node.attrib["type"]
#                            print sub_operator.type

                            if sub_operator.type ==  "variable":
                                sub_operator.name = sub_operator_node.text
                                sub_operator.operation = 0
                                if sub_operator.name not in self.variables:
                                    self.variables.append(sub_operator.name)
                                if sub_operator.name not in subop.variables:
                                    subop.variables.append(sub_operator.name)

#                                print sub_operator.name
                            elif sub_operator.type == "literal":
                                sub_operator.value = sub_operator_node.text
                                sub_operator.operation = 0
#                                print sub_operator.value

                            subop.operators.append(sub_operator)

                    elif operator.type == "literal":
                        operator.value = operator_node.text
                        operator.operation = 0


                    op.operators.append(operator)

                    if row.attrib["name"] not in self.headers:
                        self.headers.append(row.attrib["name"])
            except:
                op = Operation("none")
                self.operations.append(op)

                operator = Operator()
                operator.type = "data"
                operator.name = row.text
                op.operators.append(operator)

                self.variables.append(operator.name)
                if operator.name not in self.headers:
                    self.headers.append(operator.name)

    def extract_value(self, values, operator):
        if operator.type == "literal":
            return

        if operator.type == "complex":
            operation = operator.operation

            oper1 = operation.operators[0]
            oper2 = operation.operators[1]

            self.extract_value(values, oper1)
            self.extract_value(values, oper2)
            result = str(operation.op(float(oper1.value), float(oper2.value)))
            operator.value = result

            return

        try:
            index = self.variables.index(operator.name)
            operator.value = values[index]
        except:
            operator.value = 0
            print "Variable %s not found" % (operator.name)

    def do_job(self):
        command = ""
        command += TABLEGEN
        command += " %s" % self.results
        for var in self.variables:
            command += " '%s'" % (var)

#        print command
        fin, fout = popen2.popen2(command)

        while 1:
            line = fin.readline().strip()
            if not line:
                break
            line_values = line.split()
            line_str = ""
            results = []
            for operation in self.operations:
                if len(results) > 0:
                    line_str = string.join(results)
                    line_str += "\n"

                result = 0
#                print operation.op_value
                if operation.op_value == "none":
                    self.extract_value(line_values, operation.operators[0])
                    result = str(operation.op())

                else:
#                    print len(operation.operators)
#                    print operation.operators[0].name
                    oper1 = operation.operators[0]
                    oper2 = operation.operators[1]

                    self.extract_value(line_values, oper1)
                    self.extract_value(line_values, oper2)
                    print self.results
                    result = str(operation.op(float(oper1.value), float(oper2.value)))
#                    print "el resultado es: " + result
                results.append(result)

            line_str = string.join(results)
            line_str += "\n"
            self.data.append(line_str)


if __name__ == '__main__':

    input_files = sys.argv[1:-1]

    for file in input_files:

        parser = Parser(file, sys.argv[-1])
        parser.set_operations()
        output = file + "_" + sys.argv[-1].split('/')[-1]

        parser.do_job()

        fout = open(output, 'w')
        variables = parser.headers

        header = string.join(variables) + "\n"
        fout.write(header)
        fout.writelines(parser.data)
        fout.close

    sys.exit(1)

