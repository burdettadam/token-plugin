import json

import pytest
from indy.ledger import build_get_schema_request
from sovtoken.constants import AMOUNT
from sovtoken.test.helpers.helper_general import utxo_from_addr_and_seq_no
from sovtokenfees.test.constants import SCHEMA_FEES_ALIAS
from sovtokenfees.test.helper import get_amount_from_token_txn, add_fees_request_with_address

from indy_common.types import Request
from sovtokenfees.test.transactions.helper import get_last_token_txn

from plenum.common.constants import TXN_METADATA, TXN_METADATA_ID, DATA
from plenum.test.helper import sdk_sign_and_submit_req, \
    sdk_get_and_check_replies

SCHEMA_FEE = 3


@pytest.fixture()
def fees():
    return {SCHEMA_FEES_ALIAS: SCHEMA_FEE}


def test_send_schema_with_fees(helpers,
                               looper,
                               nodeSetWithIntegratedTokenPlugin,
                               sdk_wallet_trustee,
                               sdk_pool_handle,
                               fees_set, address_main, mint_tokens):
    req = helpers.request.schema_new(sdk_wallet=sdk_wallet_trustee)
    amount = get_amount_from_token_txn(mint_tokens)
    init_seq_no = 1
    utxos = [{"source": utxo_from_addr_and_seq_no(address_main, init_seq_no),
              AMOUNT: amount}]
    req = Request(**json.loads(req))
    req = add_fees_request_with_address(
        helpers,
        fees_set,
        req,
        address_main,
        utxos=utxos
    )

    token_len = len(nodeSetWithIntegratedTokenPlugin[0].ledgers[-1])
    write_rep = helpers.sdk.send_and_check_request_objects([req], wallet=sdk_wallet_trustee)
    assert token_len == len(nodeSetWithIntegratedTokenPlugin[0].ledgers[-1]) - 1
    assert get_last_token_txn(nodeSetWithIntegratedTokenPlugin)[1]['txn']['data']['fees'] == SCHEMA_FEE

    schema_id = write_rep[0][1]['result'][TXN_METADATA][TXN_METADATA_ID]
    request = looper.loop.run_until_complete(build_get_schema_request(sdk_wallet_trustee[1], schema_id))
    read_rep = sdk_get_and_check_replies(looper,
                                         [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert req.operation[DATA] == read_rep[0][1]['result'][DATA]
