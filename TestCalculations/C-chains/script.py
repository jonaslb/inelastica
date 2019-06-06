#!/usr/bin/env python
from itertools import combinations
import numpy as np
import netCDF4 as nc

import Inelastica.EigenChannels as EC
import Inelastica.pyTBT as TBT
import Inelastica.Phonons as P
import Inelastica.iets as IETS
import Inelastica.info as info

ver = info.label

ietss = []

# Loop over the three orientations of the carbon chain
for d in ['A1', 'A2', 'A3']:

    # Eigenchannels
    my_argv = '-f %s/TSrun/RUN.fdf %s/%s/ECscript' % (d, d, ver)
    opts = EC.GetOptions(my_argv)
    EC.main(opts)

    # pyTBT
    my_argv = '--Emin=-5.0 --Emax=5.0 -N 11 -f %s/TSrun/RUN.fdf %s/%s/TBTscript' % (d, d, ver)
    opts = TBT.GetOptions(my_argv)
    TBT.main(opts)

    # Phonons
    my_argv = '--FCwildcard=%s/FC* --OSdir=%s/OSrun' % (d, d)
    my_argv += ' --FCfirst=9 --FClast=9 --DeviceFirst=8 --DeviceLast=13 -c %s/%s/PHscript' % (d, ver)
    opts = P.GetOptions(my_argv)
    P.main(opts)

    # IETS
    my_argv = '-F 8 -L 13 -p %s/%s/PHscript/Output.nc -f %s/TSrun/RUN.fdf %s/%s/INscript' % (d, ver, d, d, ver)
    opts = IETS.GetOptions(my_argv)
    IETS.main(opts)

    # IETS with tbtrans self-energies
    args = "-F 8 -L 13 -p {d}/{ver}/PHscript/Output.nc --tbtse {d}/TSrun/device.TBT.SE.nc -f {d}/TSrun/RUN.fdf "\
           "{d}/{ver}/IN_tbtse_script"
    args = args.format(d=d, ver=ver)
    opts = IETS.GetOptions(args)
    IETS.main(opts)

    # Validate the two IETS are equal
    d0 = nc.Dataset('%s/%s/INscript/device.IN.nc' % (d, ver))
    iets0 = d0.variables["IETS"][:]
    d1 = nc.Dataset("{d}/{ver}/IN_tbtse_script/device.IN.nc".format(d=d, ver=ver))
    iets1 = d1.variables["IETS"][:]

    # print(np.max(np.abs(iets0-iets1)))
    # Found 4e-4 deviation (for A1) in practice.
    assert np.allclose(iets0, iets1, atol=1e-3)

    # For comparison between A1,2,3
    ietss.append(iets1)

for (i, iets1), (j, iets2) in combinations(enumerate(ietss), 2):
    assert np.allclose(iets1, iets2, atol=1e-3), (i, j)
