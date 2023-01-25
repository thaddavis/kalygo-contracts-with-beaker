from beaker.consts import Algos
from pyteal import (
    abi,
    TealType,
    Global,
    Int,
    Seq,
    Approve,
    Reject,
    If,
    Subroutine,
    Expr,
    Balance,
    Or,
    And,
    Addr,
    Txn,
)
from beaker.application import Application


class Subroutine__Guard_Buyer_Set_Arbitration__Mixin(Application):
    def guard_buyer_set_arbitration(
        self,
    ):
        return Seq(
            Or(
                And(
                    Global.group_size() == Int(1),
                    self.global_buyer.get() == Txn.sender()  # type: ignore
                    # App.globalGet(GLOBAL_BUYER) == Txn.sender(),
                    # Txn.application_args[0] == BUYER_SET_ARBITRATION,
                    # App.globalGet(GLOBAL_ENABLE_TIME_CHECKS) == Int(1),
                    # Global.latest_timestamp() < App.globalGet(GLOBAL_CLOSING_DATE),
                ),
                And(
                    Int(0)
                ),  # CHECK IF OTHER PARTY HAS RAISED ARBITRATION IN WHICH CASE ALLOW EXTENSION TO RAISE ARB FLAG
            )
        )
