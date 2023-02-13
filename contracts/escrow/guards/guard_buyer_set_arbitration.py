from beaker.consts import Algos
from pyteal import *
from beaker.application import Application
from ..constants import *


@Subroutine(TealType.uint64)
def guard_buyer_set_arbitration(acct: Expr):
    return Seq(
        Or(
            And(
                Global.group_size() == Int(1),
                App.globalGet(GLOBAL_BUYER) == acct,
                Global.latest_timestamp() < App.globalGet(GLOBAL_CLOSING_DATE),
            ),
            And(
                Int(0)
            ),  # TODO CHECK IF OTHER PARTY HAS RAISED ARBITRATION IN WHICH CASE ALLOW EXTENSION TO RAISE ARB FLAG
        )
    )
