# type: ignore

from typing import Final, Literal
from pyteal import *
from pyteal.ast.bytes import Bytes
from beaker.application import Application
from beaker.client.application_client import ApplicationClient
from beaker.decorators import external, create, delete, Authorize, update
from beaker.lib.storage import Mapping, List
from beaker import sandbox
from beaker.state import ApplicationStateValue
import json

from .constants import *

from .guards.guard_withdraw_escrow_balance import guard_withdraw_escrow_balance
from .guards.guard_withdraw_balance import guard_withdraw_balance
from .guards.guard_buyer_set_arbitration import guard_buyer_set_arbitration
from .guards.guard_delete_buyer_note_box import guard_delete_buyer_note_box
from .guards.guard_edit_buyer_note_box import guard_edit_buyer_note_box
from .guards.guard_delete_seller_note_box import guard_delete_seller_note_box
from .guards.guard_edit_seller_note_box import guard_edit_seller_note_box
from .guards.guard_buyer_set_pullout import guard_buyer_set_pullout
from .guards.guard_optin_to_ASA import guard_optin_to_ASA
from .guards.guard_optout_from_ASA import guard_optout_from_ASA
from .guards.guard_seller_set_arbitration import guard_seller_set_arbitration


# class SplitParty(abi.NamedTuple):
#     basis_points: abi.Field[abi.Uint8]
#     pk: abi.Field[abi.Address]

# class Note(abi.NamedTuple):
#     message: abi.Field[abi.String]


class ContractUpdate(abi.NamedTuple):
    buyer: abi.Field[abi.Address]
    seller: abi.Field[abi.Address]
    escrow_1: abi.Field[abi.Uint64]
    escrow_2: abi.Field[abi.Uint64]
    total_price: abi.Field[abi.Uint64]


class EscrowContract(Application):
    buyer_metadata = Mapping(abi.String, abi.StaticBytes[Literal[2049]])

    seller_metadata = Mapping(abi.String, abi.StaticBytes[Literal[2050]])

    global_buyer_pullout_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    global_buyer_arbitration_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    global_seller_arbitration_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )

    # stores proposed contract_update
    global_buyer_update: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.bytes
    )
    # stores proposed contract_update
    global_seller_update: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.bytes
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
            self.global_buyer.set(global_buyer.get()),
            self.global_seller.set(global_seller.get()),
            self.global_asa_id.set(global_asa_id.get()),
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
                    self.global_escrow_payment_1.set(global_escrow_payment_1.get()),
                    self.global_escrow_payment_2.set(global_escrow_payment_2.get()),
                    self.global_total_price.set(global_total_price.get()),
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

    @update
    def update(self):
        return Reject()  # Approve() for testing tho is nice : )

    @delete
    def delete(self):
        return (
            If(Balance(Global.current_application_address()) == Int(0))
            .Then(Approve())
            .Else(Reject())
        )

    @external(authorize=guard_edit_buyer_note_box)
    def edit_buyer_note_box(self, notes: abi.String):
        return Seq(
            self.buyer_metadata[Bytes("Buyer")].set(notes.get()),
            Approve(),
        )

    @external(authorize=guard_delete_buyer_note_box)
    def delete_buyer_note_box(self):
        result = App.box_delete(Bytes("Buyer"))
        return Seq(
            Assert(result == Int(1)),
            Approve(),
        )

    @external(authorize=guard_edit_seller_note_box)
    def edit_seller_note_box(self, notes: abi.String):
        return Seq(
            self.seller_metadata[Bytes("Seller")].set(notes.get()),
            Approve(),
        )

    @external(authorize=guard_delete_seller_note_box)
    def delete_seller_note_box(self):
        result = App.box_delete(Bytes("Seller"))
        return Seq(
            Assert(result == Int(1)),
            Approve(),
        )

    @external(authorize=guard_buyer_set_arbitration)
    def buyer_set_arbitration(self):
        return Seq(
            self.global_buyer_arbitration_flag.set(Int(1)),
            Approve(),
        )

    @external(authorize=guard_buyer_set_pullout)
    def buyer_set_pullout(self):
        return Seq(
            self.global_buyer_pullout_flag.set(Int(1)),
            Approve(),
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

    @external(authorize=guard_seller_set_arbitration)
    def seller_set_arbitration(self):
        return Seq(
            self.global_seller_arbitration_flag.set(Int(1)),
            Approve(),
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

    @external()
    def buyer_request_contract_update(
        self,
        global_buyer: abi.Address,
        global_seller: abi.Address,
        global_escrow_payment_1: abi.Uint64,
        global_escrow_payment_2: abi.Uint64,
        global_total_price: abi.Uint64,
    ):
        return Seq(
            (rec := ContractUpdate()).set(
                global_buyer,
                global_seller,
                global_escrow_payment_1,
                global_escrow_payment_2,
                global_total_price,
            ),
            self.global_buyer_update.set(rec.encode()),
            Approve(),
        )

    @external()
    def seller_request_contract_update(
        self,
        buyer: abi.Address,
        seller: abi.Address,
        escrow_payment_1: abi.Uint64,
        escrow_payment_2: abi.Uint64,
        total_price: abi.Uint64,
    ):
        return Seq(
            (rec := ContractUpdate()).decode(self.global_buyer_update.get()),
            (rec_buyer := abi.Address()).set(rec.buyer),
            (rec_seller := abi.Address()).set(rec.seller),
            (rec_escrow_1 := abi.Uint64()).set(rec.escrow_1),
            (rec_escrow_2 := abi.Uint64()).set(rec.escrow_2),
            (rec_total_price := abi.Uint64()).set(rec.total_price),
            If(
                And(
                    rec_buyer.get() == buyer.get(),
                    rec_seller.get() == seller.get(),
                    rec_escrow_1.get() == escrow_payment_1.get(),
                    rec_escrow_2.get() == escrow_payment_2.get(),
                    rec_total_price.get() == total_price.get(),
                )
            )
            .Then(
                Seq(
                    self.global_buyer.set(buyer.get()),
                    self.global_seller.set(seller.get()),
                    self.global_escrow_payment_1.set(escrow_payment_1.get()),
                    self.global_escrow_payment_2.set(escrow_payment_2.get()),
                    self.global_total_price.set(total_price.get()),
                )
            )
            .Else(
                Seq(
                    (rec := ContractUpdate()).set(
                        buyer,
                        seller,
                        escrow_payment_1,
                        escrow_payment_2,
                        total_price,
                    ),
                    self.global_seller_update.set(rec.encode()),
                )
            ),
            Approve(),
        )
