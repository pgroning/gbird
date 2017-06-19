from IPython.core.debugger import Tracer
import time

import numpy as np
import sys

from lib.libADDC import ADDC
from btf_a10xm import rfact_nodal  # using the same algorithm as for A10XM


def btf_a10b(POW3):
    """Calculating BTF for A10B"""
    
    # Import addc from shared lib
    fuetype = "A10B"
    acObj = ADDC(fuetype)
    AC = acObj.ac
    DOX = rfact_nodal(POW3, AC)
    return DOX
    

if __name__ == '__main__':
    POW3 = sys.argv[1]
    btf_a10b(POW3)
    
