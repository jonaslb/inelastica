from collections import namedtuple
from functools import lru_cache
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
            nua=self.tbt.na_d,
            nuo=self.tbt.no_d
            )
        self.semiinf = semiinf  # Inelastica uses this value (axis/direction) for some kpoint setup hokus pokus
        self.scaling = scaling
        # Info printing:
        print(f"Created a sisl-loaded SelfEnergy from {filename} with electrodes"
              f" {[self.tbt.elecs[e] for e in self.elecs]}, voltage={self.voltage}.")
        self.orbs = np.unique(
            np.concatenate([self.tbt.pivot(e, sort=True) for e in self.elecs])
            )
        print(f"    This self-energy lives on orbitals (full geom basis) {si.utils.list2str(self.orbs)}")
        self.atoms = self.tbt.geom.o2a(self.orbs, unique=True)
        print(f"    - corresponding to atoms {si.utils.list2str(self.atoms)}")

        # inelastica likes to repeat calls especially for ee=0+i*zeta
        self._se_hashable = lru_cache(maxsize=4)(self._se_hashable_nolru)

    # def self_energy(self, *args, **kwargs):
    #     return self.scaling * self.tbt.self_energy(self.elec, *args, **kwargs)
    #
    # def pivot(self, *args, **kwargs):
    #     return self.tbt.pivot(self.elec, *args, **kwargs)

    def _se_hashable_nolru(self, elec, ee, k, sort):
        # print("_se_hashable called,", elec)
        ee = np.array(ee)
        return self.tbt.self_energy(elec, ee-self.voltage, k=k, sort=sort)

    def getSig(self, ee,
               qp=[0, 0], left=True,
               Bulk=False, ispin=0, UseF90helpers=True,
               etaLead=0.0, useSigNCfiles=False,
               ):
        """Imitate the Inelastica.NEGF.SelfEnergy.getSig function."""
        # print("getSig", self.elecs, "called: ", ee, qp, left, Bulk, etaLead, useSigNCfiles)
        if Bulk:
            raise ValueError("The tbt self-energy does not contain the original hamilton")
        if ispin != 0:
            raise ValueError("Spin support not implemented...")
        se_big = np.zeros([self.tbt.no_d] * 2, dtype=np.complex)

        for elec in self.elecs:
            # se = self.tbt.self_energy(elec, ee-self.voltage, k=list(qp) + [0], sort=True)
            se = self._se_hashable(elec, ee-self.voltage, k=tuple(list(qp) + [0]), sort=True)
            se *= self.scaling
            pvt = self.tbt.pivot(elec, in_device=True, sort=True).reshape(-1, 1)
            se_big[pvt, pvt.T] += se

        return se_big


if raise_on_init:
    def new_init(self, *args, **kwargs):
        raise ImportError("Sisl could not be imported! Is it installed?")
    TBTSelfEnergy.__init__ = new_init
