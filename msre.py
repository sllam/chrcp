
from msrex.frontend.process import process_msre
from msrex.frontend.code.code_generator import CPPCodeGenerator

from msrex.misc.msr_logging import init_logger, log_info

from string import split
from argparse import ArgumentParser


arg_parser = ArgumentParser(prog='msre.py')
arg_parser.add_argument('filename')
# arg_parser.add_argument('-o', dest="output")
args = arg_parser.parse_args()

output = process_msre(args.filename)

if output["valid"]:
	prog = output["prog"]
	print prog
	cppGen = CPPCodeGenerator(prog, prog.fact_dir)
	cppGen.generate()
else:
	for report in output['error_reports']:
		print "\n"
		print report
		print "\n"

# mpiCC mergesort.cpp -lboost_mpi -lboost_serialization -o mergesort


