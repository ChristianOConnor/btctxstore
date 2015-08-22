# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from __future__ import print_function
from __future__ import unicode_literals


import base64
from pycoin.key import Key
from pycoin.tx.Tx import Tx
from pycoin.serialize import b2h, h2b, h2b_rev
from pycoin.tx.script import tools
from pycoin.encoding import bitcoin_address_to_hash160_sec
from pycoin.encoding import wif_to_secret_exponent
from pycoin.tx.TxOut import TxOut
from pycoin.tx.TxIn import TxIn
from pycoin.key import validate

from . import exceptions
from . import common


# TODO decorator to validate all io json serializable
# TODO use apigen when it supports python3


def unicode_str(string):
    if type(string) != type(u"unicode"):
        raise exceptions.InvalidInput("String must be a unicode string!")
    return string


def bytes_str(s):
    if type(s) not in [type("string"), type(b"bytes"), type(u"unicode")]:
        raise exceptions.InvalidInput("Must be a string!")
    if not isinstance(s, bytes):
        return s.encode('utf-8')
    return s


def tx(rawtx):
    return Tx.tx_from_hex(rawtx)


def signedtx(rawtx):
    # FIXME validate tx is signed
    return Tx.tx_from_hex(rawtx)


def unsignedtx(rawtx):
    # FIXME validate tx is unsigned
    return Tx.tx_from_hex(rawtx)


def binary(hexdata):
    if isinstance(hexdata, bytes):
        hexdata = hexdata.decode("ascii")
    return h2b(hexdata)


def signature(sig):
    sig = base64.b64decode(sig)
    if len(sig) != 65:
        raise exceptions.InvalidInput("Signature must be 65 bytes long!")
    return sig


def integer(number):
    return int(number)


def flag(flag):
    return bool(flag)


def positive_integer(number):
    number = int(number)
    if number < 0:
        raise exceptions.InvalidInput("Integer may not be < 0!")
    return number


def txid(txhash):
    return h2b_rev(txhash)


def address(testnet, address):
    address = unicode_str(address)
    netcode = 'XTN' if testnet else 'BTC'
    if not validate.is_address_valid(address, allowable_netcodes=[netcode]):
        raise exceptions.InvalidAddress(address)
    return address


def addresses(testnet, addresses):
    return list(map(lambda addr: address(testnet, addr), addresses))


def txin(txhash, index):
    txhash = txid(txhash)
    index = positive_integer(index)
    return TxIn(txhash, index)


def txout(testnet, target_address, value):
    testnet = flag(testnet)
    target_address = address(testnet, target_address)
    value = positive_integer(value)
    prefix = b'\x6f' if testnet else b"\0"
    hash160 = b2h(bitcoin_address_to_hash160_sec(target_address, prefix))
    script_text = "OP_DUP OP_HASH160 %s OP_EQUALVERIFY OP_CHECKSIG" % hash160
    script_bin = tools.compile(script_text)
    return TxOut(value, script_bin)


def txins(data):
    return list(map(lambda x: txin(x['txid'], x['index']), data))


def txouts(testnet, data):
    return list(map(lambda x: txout(testnet, x['address'], x['value']), data))


def nulldata_txout(hexdata):
    data = binary(hexdata)
    if len(data) > common.MAX_NULLDATA:
        raise exceptions.MaxNulldataExceeded(len(data), common.MAX_NULLDATA)
    script_text = "OP_RETURN %s" % b2h(data)
    script_bin = tools.compile(script_text)
    return TxOut(0, script_bin)


def hash160data_txout(hexdata, dust_limit=common.DUST_LIMIT):
    data = binary(hexdata)
    if len(data) != 20:  # 160 bit
        raise exceptions.InvalidHash160DataSize(len(data))
    script_text = "OP_DUP OP_HASH160 %s OP_EQUALVERIFY OP_CHECKSIG" % b2h(data)
    script_bin = tools.compile(script_text)
    return TxOut(dust_limit, script_bin)


def secret_exponents(testnet, wifs):
    valid_prefixes = [b'\xef' if testnet else b'\x80']
    return list(map(lambda x: wif_to_secret_exponent(x, valid_prefixes), wifs))


def key(testnet, wif):
    wif = unicode_str(wif)
    netcode = 'XTN' if testnet else 'BTC'
    if not validate.is_wif_valid(wif, allowable_netcodes=[netcode]):
        raise exceptions.InvalidWif(wif)
    return Key.from_text(wif)


def keys(testnet, wifs):
    return list(map(lambda wif: key(testnet, wif), wifs))
