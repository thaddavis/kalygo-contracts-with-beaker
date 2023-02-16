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
    guard_byr_set_arbitration,
    guard_delete_byr_note_box,
    guard_edit_byr_note_box,
    guard_delete_slr_note_box,
    guard_edit_slr_note_box,
    guard_byr_set_pullout,
    guard_optin_to_ASA,
    guard_optout_from_ASA,
    guard_slr_set_arbitration,
    guard_request_contract_update,
)


class ContractUpdate(abi.NamedTuple):
    byr: abi.Field[abi.Address]
    slr: abi.Field[abi.Address]
    escrow_1: abi.Field[abi.Uint64]
    escrow_2: abi.Field[abi.Uint64]
    total: abi.Field[abi.Uint64]
    inspect_start_date: abi.Field[abi.Uint64]
    inspect_end_date: abi.Field[abi.Uint64]
    inspect_extension_date: abi.Field[abi.Uint64]
    moving_date: abi.Field[abi.Uint64]
    closing_date: abi.Field[abi.Uint64]
    free_funds_date: abi.Field[abi.Uint64]


class EscrowContract(Application):
    byr_metadata = Mapping(abi.String, abi.StaticBytes[Literal[2049]])

    slr_metadata = Mapping(abi.String, abi.StaticBytes[Literal[2050]])

    glbl_byr_pullout_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    glbl_byr_arbitration_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    glbl_slr_arbitration_flag: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.uint64, default=Int(0)
    )
    glbl_byr_update: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.bytes
    )
    glbl_slr_update: ApplicationStateValue = ApplicationStateValue(
        stack_type=TealType.bytes
    )
    glbl_byr: ApplicationStateValue = ApplicationStateValue(stack_type=TealType.bytes)
    glbl_slr: ApplicationStateValue = ApplicationStateValue(stack_type=TealType.bytes)
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
        glbl_byr: abi.Address,
        glbl_slr: abi.Address,
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
            self.glbl_byr.set(glbl_byr.get()),
            self.glbl_slr.set(glbl_slr.get()),
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

    @external(authorize=guard_edit_byr_note_box)
    def edit_byr_note_box(self, notes: abi.String):
        return Seq(
            self.byr_metadata[Bytes("Buyer")].set(notes.get()),
            Approve(),
        )

    @external(authorize=guard_delete_byr_note_box)
    def delete_byr_note_box(self):
        result = App.box_delete(Bytes("Buyer"))
        return Seq(
            Assert(result == Int(1)),
            Approve(),
        )

    @external(authorize=guard_edit_slr_note_box)
    def edit_slr_note_box(self, notes: abi.String):
        return Seq(
            self.slr_metadata[Bytes("Seller")].set(notes.get()),
            Approve(),
        )

    @external(authorize=guard_delete_slr_note_box)
    def delete_slr_note_box(self):
        result = App.box_delete(Bytes("Seller"))
        return Seq(
            Assert(result == Int(1)),
            Approve(),
        )

    @external(authorize=guard_byr_set_arbitration)
    def byr_set_arbitration(self):
        return Seq(
            self.glbl_byr_arbitration_flag.set(Int(1)),
            Approve(),
        )

    @external(authorize=guard_byr_set_pullout)
    def byr_set_pullout(self):
        return Seq(
            self.glbl_byr_pullout_flag.set(Int(1)),
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

    @external(authorize=guard_slr_set_arbitration)
    def slr_set_arbitration(self):
        return Seq(
            self.glbl_slr_arbitration_flag.set(Int(1)),
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

    # @external(authorize=guard_byr_request_contract_update)
    # def request_contract_update(
    #     self,
    #     byr: abi.Address,
    #     slr: abi.Address,
    #     escrow_1: abi.Uint64,
    #     escrow_2: abi.Uint64,
    #     total: abi.Uint64,
    #     inspect_start_date: abi.Uint64,
    #     inspect_end_date: abi.Uint64,
    #     inspect_extension_date: abi.Uint64,
    #     moving_date: abi.Uint64,
    #     closing_date: abi.Uint64,
    #     free_funds_date: abi.Uint64,
    # ):
    #     return Seq(
    #         (rec_slr := ContractUpdate()).decode(
    #             self.glbl_slr_update.get()
    #         ),  # Get other party proposed revision
    #         If(Len(self.glbl_slr_update.get()) > Int(0))
    #         .Then(
    #             If(
    #                 And(
    #                     rec_slr.byr.use(lambda value: value.get() == byr.get()),
    #                     rec_slr.slr.use(lambda value: value.get() == slr.get()),
    #                     rec_slr.escrow_1.use(
    #                         lambda value: value.get() == escrow_1.get()
    #                     ),
    #                     rec_slr.escrow_2.use(
    #                         lambda value: value.get() == escrow_2.get()
    #                     ),
    #                     rec_slr.total.use(lambda value: value.get() == total.get()),
    #                     rec_slr.inspect_start_date.use(
    #                         lambda value: value.get() == inspect_start_date.get()
    #                     ),
    #                     rec_slr.inspect_end_date.use(
    #                         lambda value: value.get() == inspect_end_date.get()
    #                     ),
    #                     rec_slr.inspect_extension_date.use(
    #                         lambda value: value.get() == inspect_extension_date.get()
    #                     ),
    #                     rec_slr.moving_date.use(
    #                         lambda value: value.get() == moving_date.get()
    #                     ),
    #                     rec_slr.closing_date.use(
    #                         lambda value: value.get() == closing_date.get()
    #                     ),
    #                     rec_slr.free_funds_date.use(
    #                         lambda value: value.get() == free_funds_date.get()
    #                     ),
    #                 )
    #             )
    #             .Then(
    #                 Seq(
    #                     self.glbl_byr.set(byr.get()),
    #                     self.glbl_slr.set(slr.get()),
    #                     self.glbl_escrow_1.set(escrow_1.get()),
    #                     self.glbl_escrow_2.set(escrow_2.get()),
    #                     self.glbl_total.set(total.get()),
    #                     self.glbl_inspect_start_date.set(inspect_start_date.get()),
    #                     self.glbl_inspect_end_date.set(inspect_end_date.get()),
    #                     self.glbl_inspect_extension_date.set(
    #                         inspect_extension_date.get()
    #                     ),
    #                     self.glbl_moving_date.set(moving_date.get()),
    #                     self.glbl_closing_date.set(closing_date.get()),
    #                     self.glbl_free_funds_date.set(free_funds_date.get()),
    #                     #
    #                     self.glbl_byr_update.set(Bytes("")),
    #                     self.glbl_slr_update.set(Bytes("")),
    #                 )
    #             )
    #             .Else(
    #                 Seq(
    #                     (rec := ContractUpdate()).set(
    #                         byr,
    #                         slr,
    #                         escrow_1,
    #                         escrow_2,
    #                         total,
    #                         inspect_start_date,
    #                         inspect_end_date,
    #                         inspect_extension_date,
    #                         moving_date,
    #                         closing_date,
    #                         free_funds_date,
    #                     ),
    #                     self.glbl_byr_update.set(rec.encode()),
    #                 )
    #             )
    #         )
    #         .Else(
    #             Seq(
    #                 (rec := ContractUpdate()).set(
    #                     byr,
    #                     slr,
    #                     escrow_1,
    #                     escrow_2,
    #                     total,
    #                     inspect_start_date,
    #                     inspect_end_date,
    #                     inspect_extension_date,
    #                     moving_date,
    #                     closing_date,
    #                     free_funds_date,
    #                 ),
    #                 self.glbl_byr_update.set(rec.encode()),
    #             )
    #         ),
    #         Approve(),
    #     )

    @external(authorize=guard_request_contract_update)
    def request_contract_update(
        self,
        byr: abi.Address,
        slr: abi.Address,
        escrow_1: abi.Uint64,
        escrow_2: abi.Uint64,
        total: abi.Uint64,
        inspect_start_date: abi.Uint64,
        inspect_end_date: abi.Uint64,
        inspect_extension_date: abi.Uint64,
        moving_date: abi.Uint64,
        closing_date: abi.Uint64,
        free_funds_date: abi.Uint64,
    ):
        rec_o_party = Seq(
            If(App.globalGet(GLOBAL_BUYER) == Txn.sender())
            .Then(
                Seq(
                    (rec_o_party_tmp := ContractUpdate()).decode(
                        self.glbl_slr_update.get()
                    ),  # Get other party proposed revision
                ),
                rec_o_party_tmp,
            )
            .Else(
                Seq(
                    (rec_o_party_tmp := ContractUpdate()).decode(
                        self.glbl_byr_update.get()
                    ),  # Get other party proposed revision
                ),
                rec_o_party_tmp,
            )
        )

        return Seq(
            rec_o_party,
            If(Len(self.glbl_byr_update.get()) > Int(0))
            .Then(
                If(
                    And(
                        rec_o_party.byr.use(lambda value: value.get() == byr.get()),
                        rec_o_party.slr.use(lambda value: value.get() == slr.get()),
                        rec_o_party.escrow_1.use(
                            lambda value: value.get() == escrow_1.get()
                        ),
                        rec_o_party.escrow_2.use(
                            lambda value: value.get() == escrow_2.get()
                        ),
                        rec_o_party.total.use(lambda value: value.get() == total.get()),
                        rec_o_party.inspect_start_date.use(
                            lambda value: value.get() == inspect_start_date.get()
                        ),
                        rec_o_party.inspect_end_date.use(
                            lambda value: value.get() == inspect_end_date.get()
                        ),
                        rec_o_party.inspect_extension_date.use(
                            lambda value: value.get() == inspect_extension_date.get()
                        ),
                        rec_o_party.moving_date.use(
                            lambda value: value.get() == moving_date.get()
                        ),
                        rec_o_party.closing_date.use(
                            lambda value: value.get() == closing_date.get()
                        ),
                        rec_o_party.free_funds_date.use(
                            lambda value: value.get() == free_funds_date.get()
                        ),
                    )
                )
                .Then(
                    Seq(
                        self.glbl_byr.set(byr.get()),
                        self.glbl_slr.set(slr.get()),
                        self.glbl_escrow_1.set(escrow_1.get()),
                        self.glbl_escrow_2.set(escrow_2.get()),
                        self.glbl_total.set(total.get()),
                        self.glbl_inspect_start_date.set(inspect_start_date.get()),
                        self.glbl_inspect_end_date.set(inspect_end_date.get()),
                        self.glbl_inspect_extension_date.set(
                            inspect_extension_date.get()
                        ),
                        self.glbl_moving_date.set(moving_date.get()),
                        self.glbl_closing_date.set(closing_date.get()),
                        self.glbl_free_funds_date.set(free_funds_date.get()),
                        #
                        self.glbl_byr_update.set(Bytes("")),
                        self.glbl_slr_update.set(Bytes("")),
                    )
                )
                .Else(
                    Seq(
                        (rec := ContractUpdate()).set(
                            byr,
                            slr,
                            escrow_1,
                            escrow_2,
                            total,
                            inspect_start_date,
                            inspect_end_date,
                            inspect_extension_date,
                            moving_date,
                            closing_date,
                            free_funds_date,
                        ),
                        self.glbl_slr_update.set(rec.encode()),
                    )
                )
            )
            .Else(
                Seq(
                    (rec := ContractUpdate()).set(
                        byr,
                        slr,
                        escrow_1,
                        escrow_2,
                        total,
                        inspect_start_date,
                        inspect_end_date,
                        inspect_extension_date,
                        moving_date,
                        closing_date,
                        free_funds_date,
                    ),
                    self.glbl_slr_update.set(rec.encode()),
                )
            ),
            Approve(),
        )
