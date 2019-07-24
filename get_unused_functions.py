#!/usr/bin/env python

# Author: Ethan Hansen <1ethanhansen@gmail.com>

# For finding unused functions in c code
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

# Import needed modules for dealing with the CLI
import subprocess
import sys

file_func_dict = {}
# Exit if no file to parse given
if (len(sys.argv) == 1):
	sys.exit("ERROR: no file loc given")
file_name = sys.argv[1]

# find .c and .h files in the directory given, and for each file exec
# ctags looking for function names and for each function only print
# (or in this case return) the function name and the file location
functions_files_byte = subprocess.check_output(
	["find {} -type f -name '*.[ch]' -exec ctags -x --c-kinds=f {{}} ';' \
	| awk '{{print $1 $4}}'".format(file_name)], shell=True)
functions_decoded = functions_files_byte.decode()
functions_files_list = functions_decoded.split("\n")

# for each function, use cscope to check if the function is called
for item in functions_files_list:
	# Split the string combo of function name and path it came from
	# into the function and the last three parts of the part
	split_up_loc = item.split("/")
	func_name = split_up_loc[0]
	if (len(func_name) == 0):
		print("Skipping empty function")
		continue
	final_file_name = "/".join(split_up_loc[-3:])

	# use csope to check where function is called in code
	out = subprocess.check_output(
		["cscope -d -f cscope.out -R -L3 {}".format(func_name)], shell=True)
	# if not called anywhere, add func to the dict
	if (len(out) == 0):
		# Check to make sure we can append to an entry that exists
		if (final_file_name in file_func_dict):
			file_func_dict[final_file_name].append(func_name)
		else:    # if doesn't exist, create new file:func_list pair
			file_func_dict[final_file_name] = [func_name]

# open the output file and write as markdown
with open("unneeded.md", "w+") as unneeded_file:
	for source_file, func_list in file_func_dict.items():
		unneeded_file.write("#  {}\n".format(source_file))
		for func in func_list:
			unneeded_file.write("* {}\n".format(func))

