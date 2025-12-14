# SPDX-FileCopyrightText: Giovanni Ricca
# SPDX-License-Identifier: Apache-2.0

# List based on build/make/target/product/security
platform_keys = [
    "bluetooth",
    "media",
    "networkstack",
    #'nfc', # Symlink of 'com.android.nfcservices' apex key.
    "platform",
    "releasekey",  # Used to sign the final zip.
    "sdk_sandbox",
    "shared",
    "testkey",
    "verity",  # Deprecated on LineageOS 21.0.
]

# List based on $OUT/obj/PACKAGING/apexkeys_intermediates/apexkeys.txt, check_keys.py and cs.android.com
apex_keys = [
    "com.android.adbd",
    "com.android.adservices",
    "com.android.adservices.api",
    "com.android.appsearch",
    "com.android.appsearch.apk",
    "com.android.art",
    "com.android.bt",
    "com.android.bluetooth",
    "com.android.btservices",
    "com.android.cellbroadcast",
    "com.android.compos",
    "com.android.configinfrastructure",
    "com.android.connectivity.resources",
    "com.android.conscrypt",
    "com.android.crashrecovery",
    "com.android.devicelock",
    "com.android.extservices",
    "com.android.federatedcompute",
    "com.android.graphics.pdf",
    "com.android.hardware",  # Used to sign multiple apexes (according to cs.android.com)
    "com.android.health.connect.backuprestore",
    "com.android.healthconnect.controller",
    "com.android.healthfitness",
    "com.android.hotspot2.osulogin",
    "com.android.i18n",
    "com.android.ipsec",
    "com.android.media",
    "com.android.mediaprovider",
    "com.android.media.swcodec",
    "com.android.nearby.halfsheet",
    "com.android.networkstack.tethering",
    "com.android.neuralnetworks",
    "com.android.nfcservices",  # Symlinked into 'nfc' platform key.
    "com.android.ondevicepersonalization",
    "com.android.os.statsd",
    "com.android.permission",
    "com.android.profiling",
    "com.android.resolv",
    "com.android.rkpd",
    "com.android.runtime",
    "com.android.safetycenter.resources",
    "com.android.scheduling",
    "com.android.sdkext",
    "com.android.support.apexer",
    "com.android.telephony",
    "com.android.telephonycore",
    "com.android.telephonymodules",
    "com.android.tethering",
    "com.android.tzdata",
    "com.android.uprobestats",
    "com.android.uwb",
    "com.android.uwb.resources",
    "com.android.virt",
    "com.android.vndk",
    "com.android.vndk.current",
    "com.android.wifi",
    "com.android.wifi.dialog",
    "com.android.wifi.resources",
    "com.google.cf",  # Used to sign multiple apexes (according to cs.android.com)
    "com.google.pixel.camera.hal",  # Pixel specific apex
    "com.google.pixel.vibrator.hal",  # Pixel specific apex
    "com.qorvo.uwb",  # Pixel specific apex
]

# List of apexes that are signed with 'com.android.hardware' (com.android.hardware.certificate.override)
apex_hardware_keys = [
    "com.android.hardware.audio",
    "com.android.hardware.authsecret",
    "com.android.hardware.biometrics.face.virtual",
    "com.android.hardware.biometrics.fingerprint.virtual",
    "com.android.hardware.boot",
    "com.android.hardware.cas",
    "com.android.hardware.contexthub",
    "com.android.hardware.dumpstate",
    "com.android.hardware.gatekeeper",
    "com.android.hardware.gnss",
    "com.android.hardware.input.processor",
    "com.android.hardware.memtrack",
    "com.android.hardware.net.nlinterceptor",
    "com.android.hardware.neuralnetworks",
    "com.android.hardware.power",
    "com.android.hardware.rebootescrow",
    "com.android.hardware.secure_element",
    "com.android.hardware.security.authgraph",
    "com.android.hardware.security.secretkeeper",
    "com.android.hardware.sensors",
    "com.android.hardware.tetheroffload",
    "com.android.hardware.thermal",
    "com.android.hardware.threadnetwork",
    "com.android.hardware.usb",
    "com.android.hardware.uwb",
    "com.android.hardware.vibrator",
    "com.android.hardware.wifi",
]

# List of apexes that are signed with 'com.google.cf' (com.google.cf.certificate.override)
apex_cf_keys = [
    "com.android.hardware.keymint.rust_cf_remote",
    "com.android.hardware.keymint.rust_cf_guest_trusty_nonsecure",
    "com.android.hardware.keymint.rust_nonsecure",
    "com.android.hardware.gatekeeper.cf_remote",
    "com.android.hardware.gatekeeper.nonsecure",
    "com.google.cf.input.config",
    "com.google.cf.oemlock",
    "com.google.cf.health",
    "com.google.cf.health.storage",
    "com.google.cf.vulkan",
    "com.google.cf.light",
    "com.google.cf.gralloc",
    "com.google.cf.confirmationui",
    "com.google.cf.nfc",
    "com.google.cf.identity",
    "com.google.cf.ir",
    "com.google.cf.bt",
    "com.google.cf.rild",
    "com.google.cf.wifi",
]

# List of apps that are signed with specific apex keys
apex_app_keys = [
    "AdServicesApk:com.android.adservices.api.certificate.override",
    "FederatedCompute:com.android.federatedcompute.certificate.override",
    "HalfSheetUX:com.android.nearby.halfsheet.certificate.override",
    "HealthConnectBackupRestore:com.android.health.connect.backuprestore.certificate.override",
    "HealthConnectController:com.android.healthconnect.controller.certificate.override",
    "OsuLogin:com.android.hotspot2.osulogin.certificate.override",
    "PdfViewer:com.android.graphics.pdf.certificate.override",
    "SafetyCenterResources:com.android.safetycenter.resources.certificate.override",
    "ServiceConnectivityResources:com.android.connectivity.resources.certificate.override",
    "ServiceUwbResources:com.android.uwb.resources.certificate.override",
    "ServiceWifiResources:com.android.wifi.resources.certificate.override",
    "WifiDialog:com.android.wifi.dialog.certificate.override",
]
