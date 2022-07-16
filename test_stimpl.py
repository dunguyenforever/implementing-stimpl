from stimpl.expression import BooleanLiteral
from stimpl.robustness import run_stimpl_robustness_tests
from stimpl.test import run_stimpl_sanity_tests

if __name__=='__main__':
  run_stimpl_sanity_tests()
  run_stimpl_robustness_tests()