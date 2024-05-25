# android_vendor_lineage-priv_keys

A cool template to sign LineageOS 20.0 > builds with `dev-keys`.

## Usage

1. Clone this repo into `vendor/lineage-priv/keys`.
2. Edit `gen_keys` script to reflect your data.
3. Run it:

```bash
./gen_keys
```

It will generate the certificates on `vendor/lineage-priv/keys` and the actual keys used to generate the certificates on `~/.android-certs/`.

It will also generate the makefiles basing on the keys defined on `_data/` folder.

Backup **AT ALL COSTS** your `~/.android-certs/` and `vendor/lineage-priv/keys` folders **AND NEVER LEAK THOSE**. Losing these keys could prevent you from updating your LineageOS builds with the same keys, so formatting data would be required. Leakage of these keys can compromise the security and authenticity of your builds, requiring a new pair of keys to be generated.

## Bonus step

You can generate a `lineageos_pubkey` that can be used to verify your builds authenticity.

To do so, go on your `~/.android-certs/` folder and run this command:

```bash
openssl rsa -in releasekey.pem -pubout -out lineageos_pubkey
```

You can now fork [LineageOS/update_verifier](https://github.com/LineageOS/update_verifier) and add your `lineageos_pubkey` on it.
