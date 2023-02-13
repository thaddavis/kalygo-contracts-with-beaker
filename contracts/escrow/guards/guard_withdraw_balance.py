from pyteal import *
from beaker.application import Application
from ..constants import *


@Subroutine(TealType.uint64)
def guard_withdraw_balance(acct: Expr):
    return Seq(
        Or(
            App.globalGet(GLOBAL_BUYER) == Txn.sender(),
            App.globalGet(GLOBAL_SELLER) == Txn.sender(),
        )
    )
