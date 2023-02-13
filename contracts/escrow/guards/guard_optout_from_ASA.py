from pyteal import *
from beaker.application import Application
from ..constants import *


@Subroutine(TealType.uint64)
def guard_optout_from_ASA(acct: Expr):
    return Seq(Int(1))
