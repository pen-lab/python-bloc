from typing import Final

from .util.singleton import Singleton
from .bloc_delegate import BlocDelegate


class BlocSupervisor(Singleton):
    delegate: Final[BlocDelegate] = None


bloc_supervisor: BlocSupervisor = BlocSupervisor()
