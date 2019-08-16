from collections import namedtuple
import numpy as np
try:
    import sisl as si
    raise_on_init = False
except ImportError:
    # Sisl is an optional dependency, so only raise on attempted use rather than on import
    raise_on_init = True


DummyHS = namedtuple("DummyHS", ["nua", "nuo"])


class TBTSelfEnergy:
    """Imitate Inelastica.NEGF.SelfEnergy, but load the self-energy from tbtrans using sisl."""
    NA1 = 1  # must be defined
    NA2 = 1

    def __init__(self, filename, elecs, voltage=0, semiinf=0, scaling=1):
        self.tbt = si.get_sile(filename)
        self.elecs = elecs
        if not isinstance(elecs, (set, list, tuple, np.ndarray)):
            self.elecs = [elecs]
        self.voltage = voltage
        self.HS = DummyHS(
            nua=len(self.tbt.na_d),
            nuo=len(self.tbt.no_d)
            )
        self.semiinf = semiinf  # Inelastica uses this value (axis/direction) for some kpoint setup hokus pokus
        self.scaling = scaling

    # def self_energy(self, *args, **kwargs):
    #     return self.scaling * self.tbt.self_energy(self.elec, *args, **kwargs)
    #
    # def pivot(self, *args, **kwargs):
    #     return self.tbt.pivot(self.elec, *args, **kwargs)

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
        se_big = np.zeros([self.tbt.no_d] * 2, dtype=np.complex)

        for elec in self.elecs:
            se = self.tbt.self_energy(elec, ee-self.voltage, k=list(qp) + [0])
            se *= self.scaling
            pvt = self.tbt.pivot(elec, in_device=True).reshape(-1, 1)
            se_big[pvt, pvt.T] = se

        return se_big


if raise_on_init:
    def new_init(self, *args, **kwargs):
        raise ImportError("Sisl could not be imported! Is it installed?")
    TBTSelfEnergy.__init__ = new_init
