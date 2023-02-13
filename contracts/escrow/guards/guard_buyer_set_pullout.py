from pyteal import *
from beaker.application import Application
from ..constants import *


@Subroutine(TealType.uint64)
def guard_buyer_set_pullout(acct: Expr):
    return Seq(
        And(
            App.globalGet(GLOBAL_BUYER) == Txn.sender(),
            Global.latest_timestamp() < App.globalGet(GLOBAL_INSPECTION_END_DATE),
        )
    )
