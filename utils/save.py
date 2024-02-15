# get root folder for saved data

import sys
import os
import time
import plistlib

GEOMETRY_DASH_SAVE_ROOT = "UNDEFINED"

if sys.platform == "win32":
    # get user localappdata folder using environment variable (should work with win10 1809+ at least?)
    localappdata = os.environ.get("LOCALAPPDATA")
    GEOMETRY_DASH_SAVE_ROOT = f"{localappdata}\\GeometryDash"
elif sys.platform == "darwin":
    GEOMETRY_DASH_SAVE_ROOT = "~/Library/Application Support/GeometryDash"
elif sys.platform == "linux":
    # what the hell?
    GEOMETRY_DASH_SAVE_ROOT = "~/.local/share/Steam/steamapps/compatdata/322170/pfx/dosdevices/c:/users/steamuser/Local Settings/Application Data/GeometryDash/" # if you see this, please know i lost my sanity long ago and that i wish it would end
else:
    print("ERROR: you are on an unsupported platform. if you are on windows or linux and this error has appeared, use a native version of python.")
    print("this program will now exit. goodbye")
    exit(1)

# gd<->plist for decoding/encoding, because robtop snorts enough coke to singlehandedly make a cartel rich
# major assumptions about the data, but this works.
# FIXME: this shit is unreadable.
def plist_requirk(input: bytes) -> bytes:
    # rename all keys...
    new = input.replace(b"<key>", b"<k>").replace(b"</key>", b"</k>") \
        .replace(b"<dict>", b"<d>").replace(b"</dict>", b"</d>") \
        .replace(b"<string>", b"<s>").replace(b"</string>", b"</s>") \
        .replace(b"<integer>", b"<i>").replace(b"</integer>", b"</i>") \
        .replace(b"<real>", b"<r>").replace(b"</real>", b"</r>") \
        .replace(b"<true />", b"<t />").replace(b"<false />", b"<f />") \
        .replace(b"<true/>", b"<t/>").replace(b"<false/>", b"<f/>") \
        .replace(b"<dict />", b"<d />").replace(b"<dict/>", b"<d/>") \
    # ...except for the first dict.
    new = new.replace(b"<d>", b"<dict>", 1)[-1::-1] \
        .replace(b">d/<", b">tcid/<", 1)[-1::-1]
    # and now, remove the doctype and add the gdver atrib.
    return new.replace(b'<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n', b'') \
    .replace(b'<plist version="1.0">', b'<plist version="1.0" gjver="2.0">')
def plist_dequirk(input: bytes) -> bytes:
    return input.replace(b"<k>", b"<key>").replace(b"</k>", b"</key>") \
        .replace(b"<d>", b"<dict>").replace(b"</d>", b"</dict>") \
        .replace(b"<s>", b"<string>").replace(b"</s>", b"</string>") \
        .replace(b"<i>", b"<integer>").replace(b"</i>", b"</integer>") \
        .replace(b"<r>", b"<real>").replace(b"</r>", b"</real>") \
        .replace(b"<t />", b"<true />").replace(b"<f />", b"<false />") \
        .replace(b"<t/>", b"<true/>").replace(b"<f/>", b"<false/>") \
        .replace(b"<d/>", b"<dict/>").replace(b"<d />", b"<dict />")

def load_save_as_dict() -> dict:
    with open(GEOMETRY_DASH_SAVE_ROOT + "/CCGameManager.dat", 'rb') as f:
        data = f.read()
        if b'<plist' in data and b'</dict>' in data:
            # decoded save! ask user to relaunch gd once before rerun.
            print("[error] you have a decoded save as your current save. please open gd and close it properly once, then re-run.")
            exit(1)
        return plistlib.loads(plist_dequirk(decode_system_save(data)))

def write_dict_as_save(save: dict):
    with open(GEOMETRY_DASH_SAVE_ROOT + "/CCGameManager.dat", 'wb') as f:
        f.write(plist_requirk(plistlib.dumps(save)))

def write_timestamped_backup():
        backups_dir = './backups'
        if not os.path.isdir(backups_dir):
            if os.path.exists(backups_dir):
                # okay, you're so funny.
                backups_dir = '.'
            os.mkdir('./backups')
        with open(GEOMETRY_DASH_SAVE_ROOT + "/CCGameManager.dat", 'rb') as f, open(f"{backups_dir}/CCGameManager_{int(time.time())}.dat", 'wb') as o:
            o.write(f.read())

# the following code is taken from https://github.com/nekitdev/gd.py.

from gzip import decompress as standard_decompress
from zlib import MAX_WBITS
from zlib import compressobj as create_compressor
from zlib import decompressobj as create_decompressor
from zlib import error as ZLibError
from string import ascii_letters, digits
from platform import system
from typing import AnyStr, Iterable, Sequence, TypeVar
from base64 import b64decode as standard_decode_base64
from base64 import b64encode as standard_encode_base64
from base64 import urlsafe_b64decode as standard_decode_base64_url_safe
from base64 import urlsafe_b64encode as standard_encode_base64_url_safe
from xor_cipher import cyclic_xor, cyclic_xor_string, xor, xor_string

SAVE_KEY = 11
DEFAULT_APPLY_XOR = True

Z_GZIP_HEADER = 0x10
Z_AUTO_HEADER = 0x20
DARWIN = system() == "Darwin"

try:
    from Crypto.Cipher import AES
except ImportError:
    AES = None  # type: ignore

AES_KEY = b"ipu9TUv54yv]isFMh5@;t.5w34E2Ry@{"

CIPHER = None if AES is None else AES.new(AES_KEY, AES.MODE_ECB)
BASE64_PAD = 4
BASE64_INVALID_TO_PAD = 1
BASE64_PADDING = b"="
ECB_PAD = 16
DEFAULT_ENCODING = "utf-8"
DEFAULT_ERRORS = "strict"
CHARACTERS = ascii_letters + digits


LAST = ~0
T = TypeVar("T")
def last(sequence: Sequence[T]) -> T:
    return sequence[LAST]
def drop_last(count: int, data: bytes) -> bytes:
    return data[:-count]
def enforce_valid_base64(data: bytes) -> bytes:
    base64_pad = BASE64_PAD
    base64_padding = BASE64_PADDING
    base64_invalid_to_pad = BASE64_INVALID_TO_PAD

    required = len(data) % base64_pad

    if required:
        if required == base64_invalid_to_pad:
            data = drop_last(base64_invalid_to_pad, data)

        else:
            data += base64_padding * (base64_pad - required)

    return data

def decode_base64(data: bytes) -> bytes:
    return standard_decode_base64(enforce_valid_base64(data))


def encode_base64(data: bytes) -> bytes:
    return standard_encode_base64(data)


def decode_base64_url_safe(data: bytes) -> bytes:
    return standard_decode_base64_url_safe(enforce_valid_base64(data))


def encode_base64_url_safe(data: bytes) -> bytes:
    return standard_encode_base64_url_safe(data)

def decode_base64_string_url_safe(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return decode_base64_url_safe(string.encode(encoding, errors)).decode(encoding, errors)


def encode_base64_string_url_safe(
    string: str, encoding: str = DEFAULT_ENCODING, errors: str = DEFAULT_ERRORS
) -> str:
    return encode_base64_url_safe(string.encode(encoding, errors)).decode(encoding, errors)

def decode_save(data: bytes, apply_xor: bool = DEFAULT_APPLY_XOR) -> bytes:
    if apply_xor:
        data = xor(data, SAVE_KEY)

    return decompress(decode_base64_url_safe(data))


def encode_save(data: bytes, apply_xor: bool = DEFAULT_APPLY_XOR) -> bytes:
    data = encode_base64_url_safe(compress(data))

    if apply_xor:
        data = xor(data, SAVE_KEY)

    return data

def decode_darwin_save(
    data: bytes, apply_xor: bool = DEFAULT_APPLY_XOR  # `apply_xor` is here for compatibility
) -> bytes:
    cipher = CIPHER

    if cipher is None:
        raise OSError  # TODO: message?

    data = cipher.decrypt(data)

    data = drop_last(last(data), data)

    return data


def encode_darwin_save(
    data: bytes,
    apply_xor: bool = DEFAULT_APPLY_XOR,  # `apply_xor` is here, again, for compatibility
) -> bytes:
    cipher = CIPHER

    if cipher is None:
        raise OSError  # TODO: message?

    pad = ECB_PAD

    required = len(data) % pad

    byte = pad - required
    data += bytes([byte] * byte)

    return cipher.encrypt(data)


if DARWIN:
    decode_system_save, encode_system_save = decode_darwin_save, encode_darwin_save

else:
    decode_system_save, encode_system_save = decode_save, encode_save

def compress(data: bytes) -> bytes:
    compressor = create_compressor(wbits=MAX_WBITS | Z_GZIP_HEADER)

    return compressor.compress(data) + compressor.flush()


def decompress(data: bytes) -> bytes:
    try:
        return standard_decompress(data)

    except (OSError, ZLibError):
        pass

    # fallback and do some other attempts
    for wbits in (
        MAX_WBITS | Z_AUTO_HEADER,
        MAX_WBITS | Z_GZIP_HEADER,
        MAX_WBITS,
    ):
        try:
            decompressor = create_decompressor(wbits=wbits)

            return decompressor.decompress(data) + decompressor.flush()

        except ZLibError:
            pass

    raise RuntimeError("Failed to decompress data.")