# type: ignore

from typing import Literal
from pyteal import *
from pyteal.ast.bytes import Bytes
from beaker.application import Application
from beaker.decorators import external, create, delete, update
from beaker.lib.storage import Mapping
from beaker.state import ApplicationStateValue

from .constants import *

from .guards import (
    guard_withdraw_escrow_balance,
    guard_withdraw_balance,
    guard_buyer_set_arbitration,
    guard_delete_buyer_note_box,
    guard_edit_buyer_note_box,
    guard_delete_seller_note_box,
    guard_edit_seller_note_box,
    guard_buyer_set_pullout,
    guard_optin_to_ASA,
    guard_optout_from_ASA,
    guard_seller_set_arbitration,
    guard_buyer_request_contract_update,
    guard_seller_request_contract_update,
)


class ContractUpdate(abi.NamedTuple):
    buyer: abi.Field[abi.Address]
    seller: abi.Field[abi.Address]
    escrow_1: abi.Field[abi.Uint64]
    escrow_2: abi.Field[abi.Uint64]
    total: abi.Field[abi.Uint64]
    # inspect_start_date: abi.Field[abi.Uint64]
    # inspect_end_date: abi.Field[abi.Uint64]
    # inspect_extension_date: abi.Field[abi.Uint64]
    # moving_date: abi.Field[abi.Uint64]
    # closing_date: abi.Field[abi.Uint64]
    # free_funds_date: abi.Field[abi.Uint64]


class EscrowContract(Application):
    buyer_metadata = Mapping(abi.String, abi.StaticBytes[Literal[2049]])

    seller_metadata = Mapping(abi.String, abi.StaticBytes[Literal[2050]])

    glbl_buyer_pullout_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    glbl_buyer_arbitration_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    glbl_seller_arbitration_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    glbl_buyer_update: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.bytes
    )
    glbl_seller_update: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.bytes
    )
    glbl_buyer: ApplicationStateValue = ApplicationStateValue(stack_type=TealType.bytes)
    glbl_seller: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.bytes
    )
    glbl_escrow_1: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    glbl_escrow_2: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    glbl_total: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    glbl_inspect_start_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    glbl_inspect_end_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    glbl_inspect_extension_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    glbl_moving_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    glbl_closing_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    glbl_free_funds_date: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )
    glbl_asa_id: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64
    )

    @create
    def create(
        self,
        glbl_buyer: abi.Address,
        glbl_seller: abi.Address,
        glbl_escrow_1: abi.Uint64,
        glbl_escrow_2: abi.Uint64,
        glbl_total: abi.Uint64,
        glbl_inspect_start_date: abi.Uint64,
        glbl_inspect_end_date: abi.Uint64,
        glbl_inspect_extension_date: abi.Uint64,
        glbl_moving_date: abi.Uint64,
        glbl_closing_date: abi.Uint64,
        glbl_free_funds_date: abi.Uint64,
        glbl_asa_id: abi.Uint64,
    ):
        return Seq(
            self.initialize_application_state(),
            self.glbl_buyer.set(glbl_buyer.get()),
            self.glbl_seller.set(glbl_seller.get()),
            self.glbl_asa_id.set(glbl_asa_id.get()),
            If(
                And(
                    glbl_escrow_1.get() >= Int(100000),  # escrow 1 uint64
                    glbl_escrow_2.get() >= Int(100000),  # escrow 2 uint64
                    (glbl_escrow_1.get() + glbl_escrow_2.get())
                    == glbl_total.get(),  # make sure escrow 1 + 2 == total
                )
            )
            .Then(
                Seq(
                    self.glbl_escrow_1.set(glbl_escrow_1.get()),
                    self.glbl_escrow_2.set(glbl_escrow_2.get()),
                    self.glbl_total.set(glbl_total.get()),
                )
            )
            .Else(Reject()),
            If(
                And(
                    glbl_inspect_start_date.get() <= glbl_inspect_end_date.get(),
                    glbl_inspect_end_date.get() <= glbl_inspect_extension_date.get(),
                    glbl_inspect_extension_date.get() <= glbl_moving_date.get(),
                    glbl_moving_date.get() <= glbl_closing_date.get(),
                    glbl_closing_date.get() <= glbl_free_funds_date.get(),
                )
            )
            .Then(
                Seq(
                    self.glbl_inspect_start_date.set(glbl_inspect_start_date.get()),  # type: ignore
                    self.glbl_inspect_end_date.set(glbl_inspect_end_date.get()),  # type: ignore
                    self.glbl_inspect_extension_date.set(glbl_inspect_extension_date.get()),  # type: ignore
                    self.glbl_moving_date.set(glbl_moving_date.get()),  # type: ignore
                    self.glbl_closing_date.set(glbl_closing_date.get()),  # type: ignore
                    self.glbl_free_funds_date.set(glbl_free_funds_date.get()),  # type: ignore
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
            self.glbl_buyer_arbitration_flag.set(Int(1)),
            Approve(),
        )

    @external(authorize=guard_buyer_set_pullout)
    def buyer_set_pullout(self):
        return Seq(
            self.glbl_buyer_pullout_flag.set(Int(1)),
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
                        TxnField.xfer_asset: self.glbl_asa_id.get(),  # stablecoin ASA
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
            self.glbl_seller_arbitration_flag.set(Int(1)),
            Approve(),
        )

    # @external(authorize=guard_withdraw_escrow_balance)
    @external()
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

    @external(authorize=guard_buyer_request_contract_update)
    def buyer_request_contract_update(
        self,
        buyer: abi.Address,
        seller: abi.Address,
        escrow_1: abi.Uint64,
        escrow_2: abi.Uint64,
        total: abi.Uint64,
        # inspect_start_date: abi.Uint64,
        # inspect_end_date: abi.Uint64,
        # inspect_extension_date: abi.Uint64,
        # moving_date: abi.Uint64,
        # closing_date: abi.Uint64,
        # free_funds_date: abi.Uint64,
    ):
        return Seq(
            (rec_slr := ContractUpdate()).decode(
                self.glbl_seller_update.get()
            ),  # Get other party proposed revision
            If(Len(self.glbl_seller_update.get()) > Int(0))
            .Then(
                If(
                    And(
                        rec_slr.buyer.use(lambda value: value.get() == buyer.get()),
                        rec_slr.seller.use(lambda value: value.get() == seller.get()),
                        rec_slr.escrow_1.use(
                            lambda value: value.get() == escrow_1.get()
                        ),
                        rec_slr.escrow_2.use(
                            lambda value: value.get() == escrow_2.get()
                        ),
                        rec_slr.total.use(lambda value: value.get() == total.get()),
                        # rec_slr.inspect_start_date.use(
                        #     lambda value: value.get() == inspect_start_date.get()
                        # ),
                        # rec_slr.inspect_end_date.use(
                        #     lambda value: value.get() == inspect_end_date.get()
                        # ),
                        # rec_slr.inspect_extension_date.use(
                        #     lambda value: value.get() == inspect_extension_date.get()
                        # ),
                        # rec_slr.moving_date.use(
                        #     lambda value: value.get() == moving_date.get()
                        # ),
                        # rec_slr.closing_date.use(
                        #     lambda value: value.get() == closing_date.get()
                        # ),
                        # rec_slr.free_funds_date.use(
                        #     lambda value: value.get() == free_funds_date.get()
                        # ),
                    )
                )
                .Then(
                    Seq(
                        self.glbl_buyer.set(buyer.get()),
                        self.glbl_seller.set(seller.get()),
                        self.glbl_escrow_1.set(escrow_1.get()),
                        self.glbl_escrow_2.set(escrow_2.get()),
                        self.glbl_total.set(total.get()),
                        # self.glbl_inspect_start_date.set(inspect_start_date.get()),
                        # self.glbl_inspect_end_date.set(inspect_end_date.get()),
                        # self.glbl_inspect_extension_date.set(
                        #     inspect_extension_date.get()
                        # ),
                        # self.glbl_moving_date.set(moving_date.get()),
                        # self.glbl_closing_date.set(closing_date.get()),
                        # self.glbl_free_funds_date.set(free_funds_date.get()),
                        #
                        self.glbl_buyer_update.set(Bytes("")),
                        self.glbl_seller_update.set(Bytes("")),
                    )
                )
                .Else(
                    Seq(
                        (rec := ContractUpdate()).set(
                            buyer,
                            seller,
                            escrow_1,
                            escrow_2,
                            total,
                            # inspect_start_date,
                            # inspect_end_date,
                            # inspect_extension_date,
                            # moving_date,
                            # closing_date,
                            # free_funds_date,
                        ),
                        self.glbl_buyer_update.set(rec.encode()),
                    )
                )
            )
            .Else(
                Seq(
                    (rec := ContractUpdate()).set(
                        buyer,
                        seller,
                        escrow_1,
                        escrow_2,
                        total,
                        # inspect_start_date,
                        # inspect_end_date,
                        # inspect_extension_date,
                        # moving_date,
                        # closing_date,
                        # free_funds_date,
                    ),
                    self.glbl_buyer_update.set(rec.encode()),
                )
            ),
            Approve(),
        )

    @external(authorize=guard_seller_request_contract_update)
    def seller_request_contract_update(
        self,
        buyer: abi.Address,
        seller: abi.Address,
        escrow_1: abi.Uint64,
        escrow_2: abi.Uint64,
        total: abi.Uint64,
        # inspect_start_date: abi.Uint64,
        # inspect_end_date: abi.Uint64,
        # inspect_extension_date: abi.Uint64,
        # moving_date: abi.Uint64,
        # closing_date: abi.Uint64,
        # free_funds_date: abi.Uint64,
    ):
        return Seq(
            (rec_byr := ContractUpdate()).decode(
                self.glbl_buyer_update.get()
            ),  # Get other party proposed revision
            If(Len(self.glbl_buyer_update.get()) > Int(0))
            .Then(
                If(
                    And(
                        rec_byr.buyer.use(lambda value: value.get() == buyer.get()),
                        rec_byr.seller.use(lambda value: value.get() == seller.get()),
                        rec_byr.escrow_1.use(
                            lambda value: value.get() == escrow_1.get()
                        ),
                        rec_byr.escrow_2.use(
                            lambda value: value.get() == escrow_2.get()
                        ),
                        rec_byr.total.use(lambda value: value.get() == total.get()),
                        # rec_byr.inspect_start_date.use(
                        #     lambda value: value.get() == inspect_start_date.get()
                        # ),
                        # rec_byr.inspect_end_date.use(
                        #     lambda value: value.get() == inspect_end_date.get()
                        # ),
                        # rec_byr.inspect_extension_date.use(
                        #     lambda value: value.get() == inspect_extension_date.get()
                        # ),
                        # rec_byr.moving_date.use(
                        #     lambda value: value.get() == moving_date.get()
                        # ),
                        # rec_byr.closing_date.use(
                        #     lambda value: value.get() == closing_date.get()
                        # ),
                        # rec_byr.free_funds_date.use(
                        #     lambda value: value.get() == free_funds_date.get()
                        # ),
                    )
                )
                .Then(
                    Seq(
                        self.glbl_buyer.set(buyer.get()),
                        self.glbl_seller.set(seller.get()),
                        self.glbl_escrow_1.set(escrow_1.get()),
                        self.glbl_escrow_2.set(escrow_2.get()),
                        self.glbl_total.set(total.get()),
                        # self.glbl_inspect_start_date.set(inspect_start_date.get()),
                        # self.glbl_inspect_end_date.set(inspect_end_date.get()),
                        # self.glbl_inspect_extension_date.set(
                        #     inspect_extension_date.get()
                        # ),
                        # self.glbl_moving_date.set(moving_date.get()),
                        # self.glbl_closing_date.set(closing_date.get()),
                        # self.glbl_free_funds_date.set(free_funds_date.get()),
                        #
                        self.glbl_buyer_update.set(Bytes("")),
                        self.glbl_seller_update.set(Bytes("")),
                    )
                )
                .Else(
                    Seq(
                        (rec := ContractUpdate()).set(
                            buyer,
                            seller,
                            escrow_1,
                            escrow_2,
                            total,
                            # inspect_start_date,
                            # inspect_end_date,
                            # inspect_extension_date,
                            # moving_date,
                            # closing_date,
                            # free_funds_date,
                        ),
                        self.glbl_seller_update.set(rec.encode()),
                    )
                )
            )
            .Else(
                Seq(
                    (rec := ContractUpdate()).set(
                        buyer,
                        seller,
                        escrow_1,
                        escrow_2,
                        total,
                        # inspect_start_date,
                        # inspect_end_date,
                        # inspect_extension_date,
                        # moving_date,
                        # closing_date,
                        # free_funds_date,
                    ),
                    self.glbl_seller_update.set(rec.encode()),
                )
            ),
            Approve(),
        )
