from .mujoco_family import MuJoCoCPU, MJX, MuJoCoWarp
from .newton_adapter import NewtonXPBD, NewtonMuJoCo
from .drake_adapter import Drake
from .brax_adapter import BraxGeneralized
from .nexus import NexusPgsHttp, NexusDiffRigidHttp

REGISTRY = {c.name: c for c in (MuJoCoCPU, MJX, MuJoCoWarp, NewtonXPBD, NewtonMuJoCo, Drake, BraxGeneralized)}
HTTP_NEXUS = {"nexus_pgs": NexusPgsHttp, "nexus_diffrigid": NexusDiffRigidHttp}
