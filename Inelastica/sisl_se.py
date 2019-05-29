from collections import namedtuple
import numpy as np
import sisl as si


DummyHS = namedtuple("DummyHS", ["nua", "nuo"])


class TBTSelfEnergy:
    """Imitate Inelastica.NEGF.SelfEnergy, but load the self-energy from tbtrans using sisl."""
    NA1 = 1  # must be defined
    NA2 = 1

    def __init__(self, filename, elec, semiinf=0):
        self.tbt = si.get_sile(filename)
        self.elec = elec
        self.voltage = 0  # hardcoded for now
        self.HS = DummyHS(
            nua=len(np.unique(self.tbt.geom.o2a(self.pivot()))),
            nuo=len(self.tbt.pivot())
            )
        self.semiinf = semiinf  # Inelastica uses this value (axis/direction) for some kpoint setup hocus pocus
        

    def self_energy(self, *args, **kwargs):
        return self.tbt.self_energy(self.elec, *args, **kwargs)

    def pivot(self, *args, **kwargs):
        return self.tbt.pivot(self.elec, *args, **kwargs)

    def getSig(self, ee,
               qp=np.array([0, 0], np.float), left=True,
               Bulk=False, ispin=0, UseF90helpers=True,
               etaLead=0.0, useSigNCfiles=False,
               ):
        """Imitate the Inelastica.NEGF.SelfEnergy.getSig function."""
