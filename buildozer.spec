[app]
title = Farm Advisor
package.name = farmadvisor
package.domain = org.farmadvisor

source.dir = .
source.include_exts = py
source.exclude_dirs = .github,bin,.buildozer

version = 1.0
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

# The app needs no internet, camera or storage access.
android.permissions =
android.api = 33
android.minapi = 21
andriod.ndk = 25b
andriod.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
