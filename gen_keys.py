#!/usr/bin/env -S PYTHONDONTWRITEBYTECODE=1 python3
# SPDX-FileCopyrightText: Giovanni Ricca
# SPDX-License-Identifier: Apache-2.0

import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from OpenSSL import crypto

from gen_keys_py import keys
from gen_keys_py.avbtool import AvbTool
from gen_keys_py.config import SUBJECTS_PARAMS

# ENV
CERTS_PATH = Path("~/.android-certs").expanduser()
# CERTS_PATH = Path('.android-certs')  # for testing only
RSA_PLATFORM_KEY_SIZE = 2048
RSA_APEX_KEY_SIZE = 4096


def extract_public_key(key_apex_path: Path, pubkey_output_path: Path):
    class Args:
        def __init__(self, key_path, output_path):
            self.key = key_path
            self.output = open(output_path, "wb")

    args = Args(key_apex_path, pubkey_output_path)

    tool = AvbTool()
    tool.extract_public_key(args)


def generate_platform_key(cert: str):
    key_platform = CERTS_PATH / f"{cert}.pem"
    x509_file = Path(f"{cert}.x509.pem")
    pk8_file = Path(f"{cert}.pk8")

    key = None

    if not key_platform.exists():
        # Generate key_platform
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, RSA_PLATFORM_KEY_SIZE)
        key_platform.write_bytes(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    if any(not path.exists() for path in [x509_file, pk8_file]):
        # Load key_platform
        if key is None:
            key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_platform.read_bytes())

        # Generate x509_file
        cert_obj = crypto.X509()
        subj = cert_obj.get_subject()
        subj.C = SUBJECTS_PARAMS["C"]
        subj.ST = SUBJECTS_PARAMS["ST"]
        subj.L = SUBJECTS_PARAMS["L"]
        subj.O = SUBJECTS_PARAMS["O"]
        subj.OU = SUBJECTS_PARAMS["OU"]
        subj.CN = SUBJECTS_PARAMS["CN"]
        subj.emailAddress = SUBJECTS_PARAMS["emailAddress"]

        cert_obj.set_serial_number(1)
        cert_obj.gmtime_adj_notBefore(0)
        cert_obj.gmtime_adj_notAfter(10000 * 24 * 60 * 60)  # 10000 days
        cert_obj.set_issuer(cert_obj.get_subject())
        cert_obj.set_pubkey(key)
        cert_obj.sign(key, "sha256")

        x509_file.write_bytes(crypto.dump_certificate(crypto.FILETYPE_PEM, cert_obj))

        # Generate pk8_file
        pkey = serialization.load_pem_private_key(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, key), password=None
        )

        pk8_der = pkey.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        pk8_file.write_bytes(pk8_der)


def generate_apex_key(apex: str):
    key_apex = Path(f"{apex}.pem")
    x509_file = Path(f"{apex}.certificate.override.x509.pem")
    pk8_file = Path(f"{apex}.certificate.override.pk8")
    avbpubkey_file = Path(f"{apex}.avbpubkey")
    pubkey_file = Path(f"{apex}.pubkey")

    key = None

    if not key_apex.exists():
        # Generate key_apex
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, RSA_APEX_KEY_SIZE)
        key_apex.write_bytes(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    if any(not path.exists() for path in [x509_file, pk8_file]) or (
        not pubkey_file.exists() and not avbpubkey_file.exists()
    ):
        # Load key_apex
        if key is None:
            key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_apex.read_bytes())

        # Generate avbpubkey_file / pubkey_file
        if apex == "com.android.vndk":
            extract_public_key(key_apex, pubkey_file)
        else:
            extract_public_key(key_apex, avbpubkey_file)

        # Generate x509_file
        cert_obj = crypto.X509()
        subj = cert_obj.get_subject()
        subj.C = SUBJECTS_PARAMS["C"]
        subj.ST = SUBJECTS_PARAMS["ST"]
        subj.L = SUBJECTS_PARAMS["L"]
        subj.O = SUBJECTS_PARAMS["O"]
        subj.OU = SUBJECTS_PARAMS["OU"]
        subj.CN = apex
        subj.emailAddress = SUBJECTS_PARAMS["emailAddress"]

        cert_obj.set_serial_number(1)
        cert_obj.gmtime_adj_notBefore(0)
        cert_obj.gmtime_adj_notAfter(10000 * 24 * 60 * 60)  # 10000 days
        cert_obj.set_issuer(cert_obj.get_subject())
        cert_obj.set_pubkey(key)
        cert_obj.sign(key, "sha256")

        x509_file.write_bytes(crypto.dump_certificate(crypto.FILETYPE_PEM, cert_obj))

        # Generate pk8_file
        pkey = serialization.load_pem_private_key(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, key), password=None
        )

        pk8_der = pkey.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        pk8_file.write_bytes(pk8_der)


def generate_keys():
    workers = mp.cpu_count()
    CERTS_PATH.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        platform_futures = [
            executor.submit(generate_platform_key, cert) for cert in keys.platform_keys
        ]
        apex_futures = [
            executor.submit(generate_apex_key, apex) for apex in keys.apex_keys
        ]

        platform_results = [future.result() for future in platform_futures]
        apex_results = [future.result() for future in apex_futures]

    return platform_results, apex_results


def generate_android_bp():
    cert_blocks = "\n\n".join(
        f"android_app_certificate {{\n"
        f'    name: "{apex}.certificate.override",\n'
        f'    certificate: "{apex}.certificate.override",\n'
        f"}}"
        for apex in keys.apex_keys
    )

    content = f"// DO NOT EDIT THIS FILE MANUALLY\n\n{cert_blocks}\n"
    Path("Android.bp").write_text(content)


def generate_keys_mk():
    mk_file = Path("keys.mk")

    sections = [
        "# DO NOT EDIT THIS FILE MANUALLY",
        "",
        "PRODUCT_CERTIFICATE_OVERRIDES := \\",
        "\n".join(
            f"    {key}:{key}.certificate.override"
            + (" \\" if i < len(keys.apex_keys) - 1 else "")
            for i, key in enumerate(keys.apex_keys)
        ),
        "",
        "PRODUCT_CERTIFICATE_OVERRIDES += \\",
        "\n".join(
            f"    {key}:com.android.hardware.certificate.override"
            + (" \\" if i < len(keys.apex_hardware_keys) - 1 else "")
            for i, key in enumerate(keys.apex_hardware_keys)
        ),
        "",
        "PRODUCT_CERTIFICATE_OVERRIDES += \\",
        "\n".join(
            f"    {key}:com.google.cf.certificate.override"
            + (" \\" if i < len(keys.apex_cf_keys) - 1 else "")
            for i, key in enumerate(keys.apex_cf_keys)
        ),
        "",
        "PRODUCT_CERTIFICATE_OVERRIDES += \\",
        "\n".join(
            f"    {key}" + (" \\" if i < len(keys.apex_app_keys) - 1 else "")
            for i, key in enumerate(keys.apex_app_keys)
        ),
        "",
        "PRODUCT_DEFAULT_DEV_CERTIFICATE := vendor/lineage-priv/keys/releasekey",
        "PRODUCT_EXTRA_RECOVERY_KEYS += vendor/lineage-priv/keys/signed",
        "PRODUCT_MAINLINE_BLUETOOTH_SEPOLICY_DEV_CERTIFICATES := $(dir $(PRODUCT_DEFAULT_DEV_CERTIFICATE))",
        "",
    ]

    mk_file.write_text("\n".join(sections))


def main():
    generate_keys()
    generate_android_bp()
    generate_keys_mk()

if __name__ == "__main__":
    main()
