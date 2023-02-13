from pyteal import *
from beaker.application import Application
from ..constants import *


@Subroutine(TealType.uint64)
def guard_edit_seller_note_box(acct: Expr):
    return Seq(
        Or(
            And(
                App.globalGet(GLOBAL_SELLER) == acct,
                Global.latest_timestamp() < App.globalGet(GLOBAL_FREE_FUNDS_DATE),
            )
        )
    )
