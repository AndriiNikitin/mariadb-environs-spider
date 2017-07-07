#!/usr/bin/python

"""
The script will try to detect CREATE TABLE definitions for partitioned tables.
If $1==0 then for each partition of detected table corresponding port and host will be injected.
Otherwise - partitions will be attempted to be stripped out (for spider node)
"""

import re
import sys
# import logging
import subprocess

# log = logging.getLogger(__name__)
# LOGFORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
# uncomment line below for detailed debugging
# logging.basicConfig(format=LOGFORMAT, level=logging.DEBUG)


"""
if (len(sys.argv)==2 and sys.argv[1]=="-h") or len(sys.argv) > 2:
	sys.stderr.write("Generate INSERT SQL command which should inserd data with statistics similar to provided results of mysql command SHOW INDEX FROM <tablename>\n")
	sys.stderr.write("usage: mysqldatagen.py ?scale? < file.sql\n")
	exit(0)

if len(sys.argv) > 2:
	sys.stderr.write("ERROR:  only one argument is expected\n")
	sys.stderr.write("start with -h flag to see help\n")
	exit(1)
"""


def print_next_environ_binding(next_environ_binding):
        portcmd = "grep port m{}*/gen_cnf.sh | head -n 1".format(next_environ_binding)
	port = subprocess.check_output(['bash','-c', portcmd])
        if not port or port.find("=") == -1 : 
		raise ValueError("Couldn't retrieve port value for environ {}".format(next_environ_binding))
	port = port.split("=")[1].strip()

        hostcmd = "grep hostname m{}*/gen_cnf.sh | head -n 1".format(next_environ_binding)
	host = subprocess.check_output(['bash','-c', hostcmd])

	if not host : 
		host = "127.0.0.1"
	else:
		host = host.split("=")[1].strip()

	sys.stdout.write(" comment 'host \"{}\" port \"{}\"'".format(host, port))


"""
"""

def parse_create_table(is_root_node):
	class States:
		OUTSIDE=0
		IN_CREATE_TABLE=1
		IN_CLAUSE_PARTITION_BY=2


	state = States.OUTSIDE
	next_environ_idx=0

	for line in sys.stdin:
#	log.debug("{0} : {1}".format(state, line.rstrip()))

		m = re.match(r'(.*)(CREATE(\s+OR\s+REPLACE)?\s+TABLE\s+[^\(]*)(.*)', line, re.I)
		if m:
			state = States.IN_CREATE_TABLE
			if m.group(1) : sys.stdout.write(m.group(1))
			if m.group(2) : sys.stdout.write(m.group(2))
			if m.group(3) : sys.stdout.write(m.group(3))
			line = "\n"
			if m.group(4) : line = m.group(4) + line
			next_environ_idx=0
	
		if state == States.IN_CREATE_TABLE and line:
			m = re.match(r'([^\;]*)(PARTITION\s+BY)([^\;]*)', line, re.I)
			if m:
				if m.group(1) : sys.stdout.write(m.group(1))
				if m.group(2) and is_root_node : sys.stdout.write(m.group(2))
				state = States.IN_CLAUSE_PARTITION_BY
				next_environ_idx=1
				line = "\n"
				if m.group(3) : line = m.group(3) + line


		if is_root_node and state == States.IN_CLAUSE_PARTITION_BY and line:
			m = re.match(r'([^\;]*)(PARTITION\s+)([^\s,\'\"]*)(\s+VALUES\s+)([^,\;\n]*)(,)?(.*)', line, re.I)
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
			next_environ_idx=0
			state = States.OUTSIDE


parse_create_table(len(sys.argv)>1 and sys.argv[1]=="0")
