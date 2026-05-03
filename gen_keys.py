#!/usr/bin/env -S PYTHONDONTWRITEBYTECODE=1 python3
# SPDX-FileCopyrightText: Giovanni Ricca
# SPDX-License-Identifier: Apache-2.0

import multiprocessing as mp
from argparse import Namespace
from concurrent.futures import Future, ProcessPoolExecutor
from pathlib import Path
from typing import Iterable

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
from OpenSSL import crypto

from gen_keys_py import keys
from gen_keys_py.avbtool import AvbTool
from gen_keys_py.config import SUBJECTS_PARAMS

# Variables
CERTS_PATH: Path = Path('~/.android-certs').expanduser()
# CERTS_PATH: Path = Path('.android-certs')  # for testing only
RSA_PLATFORM_KEY_SIZE: int = 2048
RSA_APEX_KEY_SIZE: int = 4096
EXPIRATION_DATE: int = 10000 * 24 * 60 * 60  # 10000 days (in seconds)


class GenKeys:
    def __init__(self, cert: str) -> None:
        self.cert: str = cert
        self.pkey: Path = CERTS_PATH / f'{cert}.pem'
        self.is_apex: bool = self.cert.startswith('com.')

    def generate_pkey(self) -> crypto.PKey:
        if self.pkey.exists():
            # Load existing pkey
            return crypto.load_privatekey(
                type=crypto.FILETYPE_PEM, buffer=self.pkey.read_bytes()
            )

        pkey_size = RSA_APEX_KEY_SIZE if self.is_apex else RSA_PLATFORM_KEY_SIZE

        # Generate pkey
        key: crypto.PKey = crypto.PKey()
        key.generate_key(type=crypto.TYPE_RSA, bits=pkey_size)
        self.pkey.write_bytes(
            data=crypto.dump_privatekey(type=crypto.FILETYPE_PEM, pkey=key)
        )

        return key

    def generate_certs(self, pkey: crypto.PKey) -> None:
        x509 = (
            Path(f'{self.cert}.certificate.override.x509.pem')
            if self.is_apex
            else Path(f'{self.cert}.x509.pem')
        )
        pk8 = (
            Path(f'{self.cert}.certificate.override.pk8')
            if self.is_apex
            else Path(f'{self.cert}.pk8')
        )

        if x509.exists() and pk8.exists():
            return

        # Create cert obj
        cert_obj: crypto.X509 = crypto.X509()
        subj: crypto.X509Name = cert_obj.get_subject()
        subj.C = SUBJECTS_PARAMS['C']
        subj.ST = SUBJECTS_PARAMS['ST']
        subj.L = SUBJECTS_PARAMS['L']
        subj.O = SUBJECTS_PARAMS['O']
        subj.OU = SUBJECTS_PARAMS['OU']
        subj.CN = self.cert if self.is_apex else SUBJECTS_PARAMS['CN']
        subj.emailAddress = SUBJECTS_PARAMS['emailAddress']

        cert_obj.set_serial_number(serial=1)
        cert_obj.gmtime_adj_notBefore(amount=0)
        cert_obj.gmtime_adj_notAfter(amount=EXPIRATION_DATE)
        cert_obj.set_issuer(issuer=cert_obj.get_subject())
        cert_obj.set_pubkey(pkey)
        cert_obj.sign(pkey, digest='sha256')

        # Generate x509
        x509_der: bytes = crypto.dump_certificate(
            type=crypto.FILETYPE_PEM, cert=cert_obj
        )

        x509.write_bytes(data=x509_der)

        # Generate pk8
        pk8_dump: PrivateKeyTypes = serialization.load_pem_private_key(
            data=crypto.dump_privatekey(type=crypto.FILETYPE_PEM, pkey=pkey),
            password=None,
        )

        pk8_der: bytes = pk8_dump.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        pk8.write_bytes(data=pk8_der)

    def generate_avbpubkey(self) -> None:
        avbpubkey: Path = Path(f'{self.cert}.avbpubkey')
        pubkey: Path = Path(f'{self.cert}.pubkey')

        if not self.is_apex or pubkey.exists() or avbpubkey.exists():
            return

        output_path: Path = (
            pubkey if self.cert == 'com.android.vndk' else avbpubkey
        )

        with output_path.open('wb') as output:
            AvbTool().extract_public_key(
                args=Namespace(key=self.pkey, output=output)
            )


def generate_key(cert: str) -> None:
    key_cert: GenKeys = GenKeys(cert=cert)

    # Generate base pkey (if needed)
    key: crypto.PKey = key_cert.generate_pkey()

    # Generate x509 & pk8 (if needed)
    key_cert.generate_certs(pkey=key)

    # Generate (avb)pubkey (if needed)
    key_cert.generate_avbpubkey()


def generate_keys() -> None:
    CERTS_PATH.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        futures: list[Future[None]] = [
            executor.submit(generate_key, cert=cert)
            for cert in keys.platform_keys
        ] + [
            executor.submit(generate_key, cert=apex) for apex in keys.apex_keys
        ]

        for future in futures:
            future.result()


def generate_android_bp() -> None:
    cert_blocks: str = '\n\n'.join(
        f'android_app_certificate {{\n'
        f'    name: "{apex}.certificate.override",\n'
        f'    certificate: "{apex}.certificate.override",\n'
        f'}}'
        for apex in keys.apex_keys
    )

    content: str = f'// DO NOT EDIT THIS FILE MANUALLY\n\n{cert_blocks}\n'
    Path('Android.bp').write_text(data=content)


def generate_keys_mk() -> None:
    def _mk_product_overrides(entries: Iterable[str]) -> str:
        return ' \\\n'.join(f'    {e}' for e in entries)

    sections: list[str] = [
        '# DO NOT EDIT THIS FILE MANUALLY',
        '',
        'PRODUCT_CERTIFICATE_OVERRIDES := \\',
        _mk_product_overrides(
            f'{k}:{k}.certificate.override' for k in keys.apex_keys
        ),
        '',
        'PRODUCT_CERTIFICATE_OVERRIDES += \\',
        _mk_product_overrides(
            f'{k}:com.android.hardware.certificate.override'
            for k in keys.apex_hardware_keys
        ),
        '',
        'PRODUCT_CERTIFICATE_OVERRIDES += \\',
        _mk_product_overrides(
            f'{k}:com.google.cf.certificate.override' for k in keys.apex_cf_keys
        ),
        '',
        'PRODUCT_CERTIFICATE_OVERRIDES += \\',
        _mk_product_overrides((k for k in keys.apex_app_keys)),
        '',
        'PRODUCT_DEFAULT_DEV_CERTIFICATE := vendor/lineage-priv/keys/releasekey',
        'PRODUCT_EXTRA_RECOVERY_KEYS += vendor/lineage-priv/keys/signed',
        'PRODUCT_MAINLINE_BLUETOOTH_SEPOLICY_DEV_CERTIFICATES := $(dir $(PRODUCT_DEFAULT_DEV_CERTIFICATE))',
        '',
    ]

    Path('keys.mk').write_text(data='\n'.join(sections))


def main() -> None:
    generate_keys()
    generate_android_bp()
    generate_keys_mk()


if __name__ == '__main__':
    main()
