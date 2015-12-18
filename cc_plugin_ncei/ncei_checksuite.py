from compliance_checker.base import BaseCheck, BaseNCCheck, Result
import cf_units
import numpy as np
from netCDF4 import Variable


class NCEIVarCheck(Variable):


