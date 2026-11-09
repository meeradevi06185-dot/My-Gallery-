[app]

# ऐप का नाम और पैकेज डिटेल्स
title = My Gallery
package.name = mygallery
package.domain = org.test

# सोर्स कोड सेटिंग्स
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# ज़रूरी लाइब्रेरीज़ (अगर आपने कोड में PIL/Pillow या KivyMD इस्तेमाल किया है तो कॉमा लगाकर जोड़ सकते हैं)
requirements = python3,kivy,pillow

# स्क्रीन सेटिंग्स
orientation = portrait
fullscreen = 0

# गैलरी ऐप के लिए स्टोरेज परमिशन (बिना # के)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES

# Android API और NDK की सही सेटिंग्स (बिना # के)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.build_tools_version = 33.0.2

# लाइसेंस अपने-आप एक्सेप्ट करने के लिए (सबसे ज़रूरी)
android.accept_sdk_license = True

# आधुनिक फोन के लिए आर्किटेक्चर (तेज़ बिल्ड के लिए)
android.archs = arm64-v8a

# बैकअप और ब्रांच सेटिंग्स
android.allow_backup = True
p4a.branch = master


[buildozer]

# पूरा लॉग देखने के लिए
log_level = 2
warn_on_root = 1
