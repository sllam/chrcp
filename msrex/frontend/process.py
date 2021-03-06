
'''
This file is part of MSR Ensemble (MSRE-X).

MSRE-X is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MSRE-X is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MSRE-X. If not, see <http://www.gnu.org/licenses/>.

MSR Ensemble (MSRE-X) Version 0.5, Prototype Alpha

Authors:
Edmund S. L. Lam      sllam@qatar.cmu.edu
Iliano Cervesato      iliano@cmu.edu

* This implementation was made possible by an NPRP grant (NPRP 09-667-1-100, Effective Programming 
for Large Distributed Ensembles) from the Qatar National Research Fund (a member of the Qatar 
Foundation). The statements made herein are solely the responsibility of the authors.
'''

from string import split

import msrex.frontend.lex_parse.ast as ast
import msrex.frontend.lex_parse.parser as p

from msrex.frontend.analyze.inspectors import Inspector

from msrex.frontend.analyze.checkers.lhs_restrict_checker import LHSRestrictChecker
from msrex.frontend.analyze.checkers.var_scope_checker import VarScopeChecker
from msrex.frontend.analyze.checkers.type_checker import TypeChecker
from msrex.frontend.analyze.extractors.fact_property_extractor import FactPropertyExtractor

from msrex.frontend.transform.rule_linearizer import RuleLinearizer
from msrex.frontend.transform.alpha_indexer import AlphaIndexer

from msrex.frontend.compile.rule_facts import FactDirectory
from msrex.frontend.compile.rules import Rule
from msrex.frontend.compile.lookup_context import LinearLookup, HashLookup, OrdLookup, MemLookup

from msrex.frontend.compile.prog_compilation import ProgCompilation

def mk_prog_name( file_name ):
	return split(file_name, ".")[0]

def process_msre(file_name):
	(source_text, decs) = p.run_parser(file_name)
	error_reports, analysis = check_validity(decs, source_text)

	output = { 'source_text'   : source_text
                 , 'decs'          : decs
                 , 'error_reports' : error_reports
                 , 'analysis'      : analysis 
                 , 'valid'         : False }

	if len(error_reports) == 0:
		transformers = [RuleLinearizer,AlphaIndexer]
		for transformer in transformers:
			tr = transformer( decs )
			tr.transform()
		prog = process_prog( decs, mk_prog_name( file_name ))
		output['valid'] = True
		output['rules'] = prog.rules
		output['fact_dir'] = prog.fact_dir
		output['prog']  = prog

	return output

def check_validity(decs, source_text):
	checkers = [LHSRestrictChecker,VarScopeChecker,TypeChecker,FactPropertyExtractor]
	reports = []
	analysis = []
	for checker in checkers:
		c = checker(decs,source_text)
		c.check()
		c.init_build_display_regions()
		reports += c.get_error_reports()
		ana = c.get_analysis()
		if ana != None:
			analysis.append( ana )
		if len(reports) > 0:
			break
	return (reports,analysis)

def process_prog( decs, prog_name ):
	# Currently assumes that there is exactly one ensemble dec and one exec dec for that emsemble.	
	inspect = Inspector()
	ensem_dec = inspect.filter_decs(decs, ensem=True)[0]
	exec_dec  = inspect.filter_decs(decs, execute=True)[0]

	# print ensem_dec
	# print exec_dec

	fact_dir, externs, rules = process_ensemble( ensem_dec )
	
	prog = ProgCompilation(ensem_dec, rules, fact_dir, externs, exec_dec, prog_name)

	return prog

def process_ensemble(ensem_dec):
	inspect = Inspector()
	facts   = inspect.filter_decs(ensem_dec.decs, fact=True)
	rules   = inspect.filter_decs(ensem_dec.decs, rule=True)
	externs = inspect.filter_decs(ensem_dec.decs, extern=True)

	# print facts
	# print rules

	fact_dir = FactDirectory( facts )

	return (fact_dir, externs, map(lambda r: Rule(r, fact_dir),rules))

