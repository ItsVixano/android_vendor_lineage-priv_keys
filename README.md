# android_vendor_lineage-priv_keys

A cool template for signing LineageOS 20.0 > builds with `dev-keys`.

## Usage

1. Clone this repo to `vendor/lineage-priv/keys` (on your synced ROM rootdir) and `cd` to it.
2. Edit both `subject` vars on `gen_keys` script to reflect your data [[ref]](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ldap/distinguished-names).
3. Run it:

```bash
$ ./gen_keys
```

It will generate the certificates (defined in the `.data/` folder) in `vendor/lineage-priv/keys`, the actual keys used to generate the certificates in `~/.android-certs/`, and regenerate the makefiles as new entries are added.

Backup **AT ALL COSTS** your `~/.android-certs/` and `vendor/lineage-priv/keys` folders **AND NEVER LEAK THOSE**. Losing these keys could prevent you from updating your LineageOS builds with the same keys, so formatting data would be required. Leakage of these keys can compromise the security and authenticity of your builds, requiring a new pair of keys to be generated.

## Bonus step

You can generate a public key which can be used to verify the authenticity of your builds:

1. Fork and clone [LineageOS/update_verifier](https://github.com/LineageOS/update_verifier)
2. Run this command:

```bash
$ openssl rsa -in ~/.android-certs/releasekey.pem -pubout -out lineageos_pubkey
```

3. Push the changes to your fork.
