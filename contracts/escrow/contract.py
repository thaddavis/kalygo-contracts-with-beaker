# type: ignore

from typing import Final
from pyteal import *
from pyteal.ast.bytes import Bytes
from beaker.application import Application
from beaker.client.application_client import ApplicationClient
from beaker.decorators import external, create, delete, Authorize
from beaker import sandbox
from beaker.state import ApplicationStateValue
import json

from .constants import (
    GLOBAL_CLOSING_DATE,
    GLOBAL_BUYER,
    GLOBAL_INSPECTION_END_DATE,
    GLOBAL_SELLER,
    GLOBAL_ASA_ID,
)


class EscrowContract(Application):

    global_buyer_pullout_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    global_buyer_arbitration_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    global_seller_arbitration_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    global_buyer: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.bytes
    )
    global_seller: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.bytes
    )
    global_escrow_payment_1: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    global_escrow_payment_2: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    global_total_price: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    global_inspection_start_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    global_inspection_end_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    global_inspection_extension_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    global_moving_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    global_closing_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    global_free_funds_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    global_asa_id: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )

    @create
    def create(
        self,
        global_buyer: abi.Address,
        global_seller: abi.Address,
        global_escrow_payment_1: abi.Uint64,
        global_escrow_payment_2: abi.Uint64,
        global_total_price: abi.Uint64,
        global_inspection_start_date: abi.Uint64,
        global_inspection_end_date: abi.Uint64,
        global_inspection_extension_date: abi.Uint64,
        global_moving_date: abi.Uint64,
        global_closing_date: abi.Uint64,
        global_free_funds_date: abi.Uint64,
        global_asa_id: abi.Uint64,
    ):
        return Seq(
            self.initialize_application_state(),
            self.global_buyer.set(global_buyer.get()),  # type: ignore
            self.global_seller.set(global_seller.get()),  # type: ignore
            self.global_asa_id.set(global_asa_id.get()),  # type: ignore
            If(
                And(
                    global_escrow_payment_1.get() >= Int(100000),  # escrow 1 uint64
                    global_escrow_payment_2.get() >= Int(100000),  # escrow 2 uint64
                    (global_escrow_payment_1.get() + global_escrow_payment_2.get())
                    == global_total_price.get(),  # make sure escrow 1 + 2 == total
                )
            )
            .Then(
                Seq(
                    self.global_escrow_payment_1.set(global_escrow_payment_1.get()),  # type: ignore
                    self.global_escrow_payment_2.set(global_escrow_payment_2.get()),  # type: ignore
                    self.global_total_price.set(global_total_price.get()),  # type: ignore
                )
            )
            .Else(Reject()),
            If(
                And(
                    global_inspection_start_date.get()
                    <= global_inspection_end_date.get(),
                    global_inspection_end_date.get()
                    <= global_inspection_extension_date.get(),
                    global_inspection_extension_date.get() <= global_moving_date.get(),
                    global_moving_date.get() <= global_closing_date.get(),
                    global_closing_date.get() <= global_free_funds_date.get(),
                )
            )
            .Then(
                Seq(
                    self.global_inspection_start_date.set(global_inspection_start_date.get()),  # type: ignore
                    self.global_inspection_end_date.set(global_inspection_end_date.get()),  # type: ignore
                    self.global_inspection_extension_date.set(global_inspection_extension_date.get()),  # type: ignore
                    self.global_moving_date.set(global_moving_date.get()),  # type: ignore
                    self.global_closing_date.set(global_closing_date.get()),  # type: ignore
                    self.global_free_funds_date.set(global_free_funds_date.get()),  # type: ignore
                )
            )
            .Else(Reject()),
        )

    @delete
    def delete(self):
        return Approve()

    @Subroutine(TealType.uint64)
    def guard_buyer_set_arbitration(acct: Expr):
        return Seq(
            Or(
                And(
                    Global.group_size() == Int(1),
                    App.globalGet(GLOBAL_BUYER) == acct,
                    # self.global_buyer.get() == acct
                    Global.latest_timestamp() < App.globalGet(GLOBAL_CLOSING_DATE),
                    # App.globalGet(GLOBAL_ENABLE_TIME_CHECKS) == Int(1)
                ),
                And(
                    Int(0)
                ),  # TODO CHECK IF OTHER PARTY HAS RAISED ARBITRATION IN WHICH CASE ALLOW EXTENSION TO RAISE ARB FLAG
            )
        )

    @external(authorize=guard_buyer_set_arbitration)
    def buyer_set_arbitration(self):
        return Seq(
            self.global_buyer_arbitration_flag.set(Int(1)),
            Approve(),
        )

    @Subroutine(TealType.uint64)
    def guard_buyer_set_pullout(acct: Expr):
        return Seq(
            And(
                App.globalGet(GLOBAL_BUYER) == Txn.sender(),
                Global.latest_timestamp() < App.globalGet(GLOBAL_INSPECTION_END_DATE),
            )
        )

    @external(authorize=guard_buyer_set_pullout)
    def buyer_set_pullout(self):
        return Seq(
            self.global_buyer_pullout_flag.set(Int(1)),
            Approve(),
        )

    @Subroutine(TealType.uint64)
    def guard_optin_to_ASA(acct: Expr):
        return Seq(
            And(
                Txn.sender() == App.globalGet(GLOBAL_BUYER),
            )
        )

    @external(authorize=guard_optin_to_ASA)
    def optin_to_ASA(self):
        return Seq(
            [
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum: TxnType.AssetTransfer,
                        TxnField.xfer_asset: App.globalGet(GLOBAL_ASA_ID),
                        TxnField.asset_amount: Int(0),
                        TxnField.sender: Global.current_application_address(),
                        TxnField.asset_receiver: Global.current_application_address(),
                        TxnField.fee: Int(0),
                    }
                ),
                InnerTxnBuilder.Submit(),
                Approve(),
            ]
        )

    @Subroutine(TealType.uint64)
    def guard_optout_from_ASA(acct: Expr):
        return Seq(Int(1))

    @external(authorize=guard_optout_from_ASA)
    def optout_from_ASA(self):
        return Seq(
            [
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum: TxnType.AssetTransfer,
                        TxnField.xfer_asset: self.global_asa_id.get(),  # stablecoin ASA
                        TxnField.asset_close_to: Global.current_application_address(),
                        TxnField.sender: Global.current_application_address(),
                        TxnField.asset_receiver: Global.current_application_address(),
                        TxnField.fee: Int(0),
                    }
                ),
                InnerTxnBuilder.Submit(),
                Approve(),
            ]
        )

    @Subroutine(TealType.uint64)
    def guard_seller_set_arbitration(acct: Expr):
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

    @external(authorize=guard_seller_set_arbitration)
    def seller_set_arbitration(self):
        return Seq(
            self.global_seller_arbitration_flag.set(Int(1)),
            Approve(),
        )

    @Subroutine(TealType.uint64)
    def guard_withdraw_escrow_balance(acct: Expr):
        return Seq(
            Or(
                App.globalGet(GLOBAL_SELLER) == Txn.sender(),
                App.globalGet(GLOBAL_BUYER) == Txn.sender(),
            )
        )

    @external(authorize=guard_withdraw_escrow_balance)
    def withdraw_escrow_balance(self):
        contract_ASA_balance = AssetHolding.balance(
            Global.current_application_address(), App.globalGet(GLOBAL_ASA_ID)
        )
        return Seq(
            [
                contract_ASA_balance,
                # ASA back to sender
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum: TxnType.AssetTransfer,
                        TxnField.xfer_asset: App.globalGet(GLOBAL_ASA_ID),
                        # vvv simulate amount of ASA to return to sender vvv
                        # TxnField.asset_amount: Btoi(Txn.application_args[2]),
                        TxnField.asset_amount: contract_ASA_balance.value(),
                        TxnField.sender: Global.current_application_address(),
                        TxnField.asset_receiver: Txn.sender(),
                        TxnField.fee: Int(0),
                    }
                ),
                InnerTxnBuilder.Submit(),
                Approve(),
            ]
        )

    @Subroutine(TealType.uint64)
    def guard_withdraw_balance(acct: Expr):
        return Seq(
            Or(
                App.globalGet(GLOBAL_BUYER) == Txn.sender(),
                App.globalGet(GLOBAL_SELLER) == Txn.sender(),
            )
        )

    @external(authorize=guard_withdraw_balance)
    def withdraw_balance():
        return Seq(
            [
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum: TxnType.Payment,
                        TxnField.amount: Balance(Global.current_application_address())
                        - Global.min_txn_fee(),
                        TxnField.sender: Global.current_application_address(),
                        TxnField.receiver: Txn.sender(),
                        TxnField.fee: Global.min_txn_fee(),
                        TxnField.close_remainder_to: Txn.sender(),
                    }
                ),
                InnerTxnBuilder.Submit(),
                Approve(),
            ]
        )
