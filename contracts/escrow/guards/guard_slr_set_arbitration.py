from pyteal import *
from beaker.application import Application
from ..constants import *


@Subroutine(TealType.uint64)
def guard_slr_set_arbitration(acct: Expr):
    return Seq(
        Or(
            And(
                App.globalGet(GLOBAL_SELLER) == Txn.sender(),
                Global.latest_timestamp() < App.globalGet(GLOBAL_CLOSING_DATE),
            ),
            And(
                Int(0)
            ),  # CHECK IF OTHER PARTY HAS RAISED ARBITRATION IN WHICH CASE ALLOW EXTENSION TO RAISE ARB FLAG
        )
    )
