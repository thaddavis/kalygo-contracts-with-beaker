from pyteal import *
from beaker.application import Application
from ..constants import *


@Subroutine(TealType.uint64)
def guard_request_contract_update(acct: Expr):
    return Seq(
        And(
            Or(
                App.globalGet(GLOBAL_SELLER) == acct,
                App.globalGet(GLOBAL_BUYER) == acct,
            ),
            Global.latest_timestamp() < App.globalGet(GLOBAL_CLOSING_DATE),
        )
    )
