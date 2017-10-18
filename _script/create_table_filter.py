#!/usr/bin/python

"""
The script will try to detect CREATE TABLE definitions for partitioned tables.
If $1==0 then for each partition of detected table corresponding port and host will be injected.
Otherwise - partitions will be attempted to be stripped out (for spider node)
$2 optionally may be file name for nodes.lst of the cluster, where first entry is root Spider node
if $2 is not provided, then m0 is root spider node and m1... are child nodes
if $2 is environ id, then all tables to be created on the same instance, 
thus sequence number is to be added to table names
"""

import re
import sys
# import logging
import subprocess

# log = logging.getLogger(__name__)
# LOGFORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
# uncomment line below for detailed debugging
# logging.basicConfig(format=LOGFORMAT, level=logging.DEBUG)

node_list_file = None
table_name=""

# i.e. $2 is environ id
def is_self_referencing():
	return re.match(r'[a-z][0-9]', node_list_file)

def print_next_environ_binding(next_environ_binding):
	# if node_list_file is environ id, then all tables to be created on the same instance
	if is_self_referencing() :
		portcmd = "grep port {}*/gen_cnf.sh | head -n 1".format(node_list_file)
		hostcmd = "grep hostname {}*/gen_cnf.sh | head -n 1".format(node_list_file)
	elif node_list_file:
		portcmd = "grep port $(tail -n+{} '{}' | head -n1)*/gen_cnf.sh | head -n 1".format(next_environ_binding+1,node_list_file)
		hostcmd = "grep hostname $(tail -n+{} '{}' | head -n1)*/gen_cnf.sh | head -n 1".format(next_environ_binding+1,node_list_file)
	else:
		portcmd = "grep port m{}*/gen_cnf.sh | head -n 1".format(next_environ_binding)
		hostcmd = "grep hostname m{}*/gen_cnf.sh | head -n 1".format(next_environ_binding)

	port = subprocess.check_output(['bash','-c', portcmd])
	if not port or port.find("=") == -1 : 
		raise ValueError("Couldn't retrieve port value for environ {}".format(next_environ_binding))
	port = port.split("=")[1].strip()

	host = subprocess.check_output(['bash','-c', hostcmd])

	if not host : 
		host = "127.0.0.1"
	else:
		host = host.split("=")[1].strip()

	# if node_list_file is environ id, then all tables to be created on the same instance
	# thus sequence number is to be added to table names
	if is_self_referencing() :
		extra=', table \"{}_{}\" '.format(table_name,next_environ_binding)
	else :
		extra=""

	sys.stdout.write(" comment 'host \"{}\", port \"{}\", user \"root\" {} '".format(host, port, extra))


def parse_create_table(is_root_node):
	class States:
		OUTSIDE=0
		IN_CREATE_TABLE=1
		IN_CLAUSE_PARTITION_BY=2


	state = States.OUTSIDE
	next_environ_idx=0
        global table_name
        table_name=""

	for line in sys.stdin:
#	log.debug("{0} : {1}".format(state, line.rstrip()))

		m = re.match(r'(.*)(CREATE(\s+OR\s+REPLACE)?\s+TABLE\s+)([^\(]*)(.*)', line, re.I)
		if m:
			state = States.IN_CREATE_TABLE
			if m.group(1) : sys.stdout.write(m.group(1))
			if m.group(2) : sys.stdout.write(m.group(2))
			if m.group(3) : sys.stdout.write(m.group(3))

                        table_name=m.group(4).strip().strip('`')
			if is_root_node or (not is_self_referencing()) or (len(sys.argv)<1):
				sys.stdout.write(m.group(4))
			else:
				# for self_referencing spider we append $1 to table name
				# so child tables  with be in format table_N
				# and could be referenced from root spider table
				sys.stdout.write(" {}_{} ".format(table_name,sys.argv[1]))

                        # discard eventual database name
                        if "." in table_name: _, table_name = table_name.split(".")
			line = "\n"
			if m.group(5) : line = m.group(5) + line
			next_environ_idx=0
			cached_engine_definition=""
	
		if state == States.IN_CREATE_TABLE and line:
			m = re.match(r'([^\;]*)(\s*ENGINE\s*(=\s*)?)([^\s,\'\"]*)(.*)', line, re.I)
			if m:
				if m.group(1) : sys.stdout.write(m.group(1))
                                sys.stdout.write(m.group(2))
                                sys.stdout.write(m.group(4))
				if is_root_node:
					cached_engine_definition += " ENGINE SPIDER COMMENT 'wrapper \"mysql\", table \"{}\" ' ".format(table_name)
                                line = m.group(5)

		if state == States.IN_CREATE_TABLE and line:
			m = re.match(r'([^\;]*)(PARTITION\s+BY)([^\;]*)', line, re.I)
			if m:
				if cached_engine_definition : 
					if is_root_node :
						sys.stdout.write(cached_engine_definition)

				if m.group(1) : sys.stdout.write(m.group(1))
				if m.group(2) and is_root_node : sys.stdout.write(m.group(2))
				state = States.IN_CLAUSE_PARTITION_BY
				next_environ_idx=1
				line = "\n"
				if m.group(3) : line = m.group(3) + line


		if is_root_node and state == States.IN_CLAUSE_PARTITION_BY and line:
			m = re.match(r'([^\;]*)(PARTITION\s+)([^\s,\'\"\)]*)(\s+VALUES\s+)?([^,\;\n]*)?(,)?(.*)', line, re.I)
			if m:
				if m.group(1) : sys.stdout.write(m.group(1))
				if m.group(2) : sys.stdout.write(m.group(2))
				if m.group(3) : sys.stdout.write(m.group(3))
				if m.group(4) : sys.stdout.write(m.group(4))
				if m.group(5) : sys.stdout.write(m.group(5))
				print_next_environ_binding(next_environ_idx)
				next_environ_idx += 1
				line = "\n"
				if m.group(7) : line = m.group(7) + line
				if m.group(6) : line = m.group(6) + line

		if line:
			if not ( not is_root_node and state == States.IN_CLAUSE_PARTITION_BY) : 
				sys.stdout.write(line)
			elif line.find(";") != -1 :
				sys.stdout.write(";")

		if line and re.match(r'(.*)(\;)(.*)', line, re.I):
			cached_engine_definition = ""
			next_environ_idx=0
			state = States.OUTSIDE
                        table_name=""

if len(sys.argv)>2 :
	node_list_file = sys.argv[2]


parse_create_table(len(sys.argv)>1 and sys.argv[1]=="0")
