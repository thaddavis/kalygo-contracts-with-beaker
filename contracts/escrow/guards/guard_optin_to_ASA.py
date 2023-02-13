from pyteal import *
from beaker.application import Application
from ..constants import *


@Subroutine(TealType.uint64)
def guard_optin_to_ASA(acct: Expr):
    return Seq(
        And(
            Txn.sender() == App.globalGet(GLOBAL_BUYER),
        )
    )
