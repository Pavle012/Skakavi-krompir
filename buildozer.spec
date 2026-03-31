[app]

# (str) Title of your application
title = Skakavi Krompir

# (str) Package name
package.name = skakavikrompir

# (str) Package domain (needed for android/ios packaging)
package.domain = io.github.Pavle012

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,wav,json

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,kivy_game/*,shared/*

# (list) Source files to exclude (let empty to include all the files)
source.exclude_exts = spec,sh,yml,xml,desktop,json,bat,md

# (list) List of directory to exclude (let empty to include all the files)
source.exclude_dirs = tests, bin, venv, .venv, .git, .github, build, dist, original, mods, example skmod

# (str) Application versioning (method 1)
version = 2.1.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,pillow,requests,openssl

# (str) Custom source folders for requirements
# Comma separated e.g. requirements.source.kivy = ../../kivy
#requirements.source.pysdl2 = ...

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/potato.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/potato.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT_TO_PY

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess downloads or network errors
#android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when installing SDK
android.accept_sdk_license = True

# (str) Android entry point, default is to use start.py
#android.entrypoint = org.kivy.android.PythonService
android.entrypoint = main.py

# (str) Android app theme, default is ok for Kivy
#android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the search for libpython
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. (Order is important)
#android.add_jars = foo.jar,bar.jar,path/to/baz.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add
#android.add_aars =

# (list) Gradle dependencies
#android.gradle_dependencies =

# (list) add python compile options to this list
#python_compile_items = pyo

# (list) add python compile options for specific architectures
#python_compile_items_optimized = pyo

# (list) List of Android architectures to build for
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >= 23)
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own recipes (if any)
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android
#p4a.bootstrap = sdl2

# (int) port number to open the telescope
#p4a.port = 4999


[buildozer]

# (int) log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (str) method of encapsulation for search (can be re or find)
#method = re

# (bool) Warning: if bin_dir is not set, the default value of .buildozer/bin will be used
#bin_dir = ./bin
