from beaker.consts import Algos
from pyteal import *
from beaker.application import Application
from ..constants import *


@Subroutine(TealType.uint64)
def guard_withdraw_escrow_balance(acct: Expr):
    contract_ASA_balance = AssetHolding.balance(
        Global.current_application_address(), App.globalGet(GLOBAL_ASA_ID)
    )
    return Seq(
        contract_ASA_balance,
        Or(
            And(
                # testing conditions under which BUYER can withdraw money
                App.globalGet(GLOBAL_BUYER) == Txn.sender(),
                App.globalGet(GLOBAL_MOVING_DATE) < Global.latest_timestamp(),
                App.globalGet(GLOBAL_BUYER_PULLOUT_FLAG) == Int(1),
                App.globalGet(GLOBAL_BUYER_ARBITRATION_FLAG) < Int(1),
                App.globalGet(GLOBAL_SELLER_ARBITRATION_FLAG) < Int(1),
                contract_ASA_balance.value() > Int(0),
            ),
            And(
                # testing conditions under which BUYER can withdraw money
                App.globalGet(GLOBAL_BUYER) == Txn.sender(),
                App.globalGet(GLOBAL_BUYER_ARBITRATION_FLAG) == Int(1),
                App.globalGet(GLOBAL_FREE_FUNDS_DATE) < Global.latest_timestamp(),
                App.globalGet(GLOBAL_SELLER_ARBITRATION_FLAG) < Int(1),
                contract_ASA_balance.value() > Int(0),
            ),
            And(
                # testing conditions under which SELLER can withdraw money
                App.globalGet(GLOBAL_SELLER) == Txn.sender(),
                App.globalGet(GLOBAL_CLOSING_DATE) < Global.latest_timestamp(),
                App.globalGet(GLOBAL_BUYER_PULLOUT_FLAG) < Int(1),
                App.globalGet(GLOBAL_BUYER_ARBITRATION_FLAG) < Int(1),
                App.globalGet(GLOBAL_SELLER_ARBITRATION_FLAG) < Int(1),
                contract_ASA_balance.value() > Int(0),
            ),
            And(
                # testing conditions under which SELLER can withdraw money
                App.globalGet(GLOBAL_SELLER) == Txn.sender(),
                App.globalGet(GLOBAL_FREE_FUNDS_DATE) < Global.latest_timestamp(),
                App.globalGet(GLOBAL_BUYER_PULLOUT_FLAG) < Int(1),
                App.globalGet(GLOBAL_BUYER_ARBITRATION_FLAG) < Int(1),
                App.globalGet(GLOBAL_SELLER_ARBITRATION_FLAG) == Int(1),
                contract_ASA_balance.value() > Int(0),
            ),
        ),
    )
