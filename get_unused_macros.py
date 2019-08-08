#!/usr/bin/env python

# Author: Ethan Hansen <1ethanhansen@gmail.com>

# For finding unused macros in c code
#
# Assumptions:
#   cscope and ctags installed
#   cscope has been used to generate cscope.out for your project        
#   cscope.out exists in the current directory
#
# Usage:
#   enter the full path to the file or files you want to check
#   eg: /home/ethan/git/linux-rcu/kernel/rcu
#   OR: /home/ethan/git/linux-rcu/kernel/rcu/rcu.h
#   if you give a dir, it will search all the .c and .h files there

# Import modules for CLI calling
import subprocess
import sys

file_var_dict = {}
# Exit the program if no file to parse given
if (len(sys.argv) == 1):
	sys.exit("ERROR: no file loc given")
file_name = sys.argv[1]

# find .c and .h files in the directory given, and for each file exec
# ctags looking for macro names and for each macro only print
# (or in this case return) the macro name and the file location
variables_files_byte = subprocess.check_output(
	["find {} -type f -name '*.[ch]' -exec ctags -x --c-kinds=d {{}} ';' \
	| awk '{{print $1 $4}}'".format(file_name)], shell=True)
variables_decoded = variables_files_byte.decode()
variables_files_list = variables_decoded.split("\n")
min_len = 10
min_list = []

for item in list(set(variables_files_list))[1:]:
	# Split the string combo of macro name and path it came from     
    # into the macro and the last three parts of the part
	split_up_loc = item.split("/")
	var_name = split_up_loc[0]
	final_file_name = "/".join(split_up_loc[-3:])

	# Some sanity checks for empty and reserved vars
	if len(var_name) == 0:
		continue
	if var_name[0] == "_":
		continue

	try:
		# Use cscope to find the C symbol in code
		out = subprocess.check_output(
			["cscope -d -f cscope.out -R -L0 {}".format(var_name)], shell=True)
	except:
		continue
	# Make the output a usable list of vars & the file they came from
	out_decoded = out.decode()
	out_list = out_decoded.split("\n")
	used = False
	# If all we found was declarations and assignments
	if len(out_list) < 3:
		# Check to make sure we can append to an entry that exists
		if final_file_name in file_var_dict:
			file_var_dict[final_file_name].append(var_name)
		else:  # If doesn't exist, create new file:var_list pair
			file_var_dict[final_file_name] = [var_name]

# Open the output file and write as markdown
with open("unneeded-macros.md", "w+") as unneeded_file:
	for source_file, var_list in file_var_dict.items():
		unneeded_file.write("# {}\n".format(source_file))
		for var in var_list:
			unneeded_file.write("* {}\n".format(var))
