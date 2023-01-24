#!/bin/bash

echo "WALLETS"

goal wallet new wallet_QWEASD

while read i; do
    asArray=($i)
    default_account=${asArray[2]}
    break
done <<< "`goal account list`"
# exit 0
echo ""
echo "Default Account: ${default_account}"
echo ""
account_a_creation_output=`goal account new -w wallet_QWEASD`
account_b_creation_output=`goal account new -w wallet_QWEASD`
account_c_creation_output=`goal account new -w wallet_QWEASD`
echo $account_a_creation_output
echo $account_b_creation_output
echo $account_c_creation_output
account_a=$(echo $account_a_creation_output | cut -c 34-91)
account_b=$(echo $account_b_creation_output | cut -c 34-91)
account_c=$(echo $account_c_creation_output | cut -c 34-91)
echo ""
echo "account_a"
echo $account_a
account_a_export_output=`goal account export -a $account_a -w wallet_QWEASD`
account_a_mneumonic=$(echo $account_a_export_output | awk -F'"' '{print $2}')
echo $account_a_mneumonic
echo ""
echo "account_b"
echo $account_b
account_b_export_output=`goal account export -a $account_b -w wallet_QWEASD`
account_b_mneumonic=$(echo $account_b_export_output | awk -F'"' '{print $2}')
echo $account_b_mneumonic
echo ""
echo "account_c"
echo $account_c
account_c_export_output=`goal account export -a $account_c -w wallet_QWEASD`
account_c_mneumonic=$(echo $account_c_export_output | awk -F'"' '{print $2}')
echo $account_c_mneumonic
echo ""

mAlgoAmount=10000000000
echo ""
goal clerk send -a $mAlgoAmount -f $default_account -t $account_a
echo ""
goal clerk send -a $mAlgoAmount -f $default_account -t $account_b
echo ""
goal clerk send -a $mAlgoAmount -f $default_account -t $account_c
echo ""
# Print Balance
account_a_balance=`goal account balance -a $account_a`
echo "account a balance: $account_a_balance"
echo ""
account_b_balance=`goal account balance -a $account_b`
echo "account b balance: $account_b_balance"
echo ""
account_c_balance=`goal account balance -a $account_c`
echo "account c balance: $account_c_balance"
echo ""

# Create Stablecoin ASA
goal asset create \
--asseturl "https://www.circle.com" \
--creator $account_c \
--decimals 2 \
--name "USDCa" \
--total 1000000000 \
--unitname "USDCa" \
--out "unsigned_asset_creation.tx"

goal clerk sign -w wallet_QWEASD -i unsigned_asset_creation.tx -o signed_asset_creation.tx
goal clerk rawsend -w wallet_QWEASD -f signed_asset_creation.tx
echo "_ _ _"

while read i; do
    echo "$i"
    asArray=($i)
    # echo ${asArray[2]}
    asset_id=${asArray[2]}
    break
done <<< "`goal asset info --creator $account_c --unitname "USDCa"`"

# OPTIN AND SEND ASA TO ACCOUNT A

goal asset optin \
--assetid $asset_id \
--account $account_a \
--wallet wallet_QWEASD

goal asset send \
--amount 1000000 \
--assetid $asset_id \
--from $account_c \
--to $account_a \
--wallet wallet_QWEASD

# OPTIN AND SEND ASA TO ACCOUNT B

goal asset optin \
--assetid $asset_id \
--account $account_b \
--wallet wallet_QWEASD

goal asset send \
--amount 1000000 \
--assetid $asset_id \
--from $account_c \
--to $account_b \
--wallet wallet_QWEASD

sed \
"
s/ACCOUNT_A_ADDRESS/$account_a/g;
s/ACCOUNT_A_MNEMONIC/$account_a_mneumonic/g;
s/ACCOUNT_B_ADDRESS/$account_b/g;
s/ACCOUNT_B_MNEMONIC/$account_b_mneumonic/g;
s/ACCOUNT_C_ADDRESS/$account_c/g;
s/ACCOUNT_C_MNEMONIC/$account_c_mneumonic/g;
s/STABLECOIN_ASA_ID/$asset_id/g;
" config/escrow_template.py > config/escrow.py
