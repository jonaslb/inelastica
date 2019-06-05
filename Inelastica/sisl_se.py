from collections import namedtuple
import numpy as np
import sisl as si


DummyHS = namedtuple("DummyHS", ["nua", "nuo"])


class TBTSelfEnergy:
    """Imitate Inelastica.NEGF.SelfEnergy, but load the self-energy from tbtrans using sisl."""
    NA1 = 1  # must be defined
    NA2 = 1

    def __init__(self, filename, elec, voltage=0, semiinf=0, scaling=1):
        self.tbt = si.get_sile(filename)
        self.elec = elec
        self.voltage = voltage
        self.HS = DummyHS(
            nua=len(np.unique(self.tbt.geom.o2a(self.pivot()))),
            nuo=len(self.tbt.pivot())
            )
        self.semiinf = semiinf  # Inelastica uses this value (axis/direction) for some kpoint setup hocus pocus
        self.scaling = scaling

    def self_energy(self, *args, **kwargs):
        return self.scaling * self.tbt.self_energy(self.elec, *args, **kwargs)

    def pivot(self, *args, **kwargs):
        return self.tbt.pivot(self.elec, *args, **kwargs)

    def getSig(self, ee,
               qp=[0, 0], left=True,
               Bulk=False, ispin=0, UseF90helpers=True,
               etaLead=0.0, useSigNCfiles=False,
               ):
        """Imitate the Inelastica.NEGF.SelfEnergy.getSig function."""
        if Bulk:
            raise ValueError("The tbt self-energy does not contain the original hamilton")
        if ispin != 0:
            raise ValueError("Spin support not implemented...")
        se = self.self_energy(ee-self.voltage, k=list(qp) + [0], sort=True)
        se_big = np.zeros([self.tbt.no_d] * 2, dtype=np.complex)
        pvt = self.pivot(in_device=True, sort=True).reshape(-1, 1)
        # print(f"IM {self.elec} and this is me indices: {pvt}")
        se_big[pvt, pvt.T] = se
        return se_big
