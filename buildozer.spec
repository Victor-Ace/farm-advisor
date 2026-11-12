[app]
title = Farm Advisor
package.name = farmadvisor
package.domain = org.farmadvisor

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,mp3
#source.exclude_dirs = .github,bin,.buildozer

version = 1.0
requirements = python3,kivy,https://github.com/kivyMD/kivyMD/archive/master.zip,materialyoucolor,exceptiongroup,asyncgui,asynckivy,pillow

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0
fullscreen = 0

# The app needs no internet, camera or storage access.
android.permissions =
android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 25b
andriod.ndk_api = 21
android.archs = arm64-v8a, armebi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
