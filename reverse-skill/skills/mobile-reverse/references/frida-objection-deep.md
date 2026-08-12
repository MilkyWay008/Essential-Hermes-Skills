# Frida + Objection Deep Usage

## Frida Core APIs

### Java Runtime (Android)

```javascript
Java.perform(function() {
    // get a class
    var String = Java.use("java.lang.String");

    // Hook a static method
    var System = Java.use("java.lang.System");
    System.getProperty.overload('java.lang.String').implementation = function(key) {
        console.log("System.getProperty: " + key);
        return this.getProperty(key);
    };

    // Hook a constructor
    var File = Java.use("java.io.File");
    File.$init.overload('java.lang.String').implementation = function(path) {
        console.log("File opened: " + path);
        return this.$init(path);
    };

    // enumerate loaded classes
    Java.enumerateLoadedClasses({
        onMatch: function(className) { console.log(className); },
        onComplete: function() {}
    });

    // modify return values
    var RootDetector = Java.use("com.app.security.RootDetector");
    RootDetector.isDeviceRooted.implementation = function() {
        return false;
    };
});
```

### Native Layer (Android + iOS)

```javascript
// Hook exported functions
Interceptor.attach(Module.findExportByName(null, "open"), {
    onEnter: function(args) {
        this.path = Memory.readUtf8String(args[0]);
    },
    onLeave: function(retval) {
        console.log("open(" + this.path + ") = " + retval);
    }
});

// Hook any address (by offset)
var base = Module.findBaseAddress("libnative.so");
var target = base.add(0x12345);
Interceptor.attach(target, {
    onEnter: function(args) {
        console.log("Function called from: " + Thread.backtrace(this.context, Backtracer.ACCURATE)
            .map(DebugSymbol.fromAddress).join('\n'));
    }
});

// modify return values
Interceptor.attach(Module.findExportByName(null, "strcmp"), {
    onLeave: function(retval) {
        if (retval.toInt32() === 0) return; // strings equal, skip
        // Force match
        retval.replace(0);
    }
});
```

### ObjC Runtime (iOS)

```javascript
// Hook ObjC methods
var hook = ObjC.classes.ViewController["- viewDidLoad"];
Interceptor.attach(hook.implementation, {
    onEnter: function(args) {
        console.log("viewDidLoad called");
    }
});

// enumerate all classes
ObjC.enumerateLoadedClasses({
    onMatch: function(className) { console.log(className); },
    onComplete: function() {}
});

// call ObjC methods
var NSString = ObjC.classes.NSString;
var str = NSString.stringWithString_("Hello from Frida");
```

## Objection Command Cheatsheet

### General

```bash
objection -g "com.app" explore           # start
objection -g "com.app" explore -q        # quiet start (inject only, don't wait)
objection patchapk --source app.apk      # auto-inject Frida Gadget
objection signapk --source app.apk       # sign only

# filesystem
env              # app data directory
ls               # list files
file download /path/to/file  # download a file
file upload local.txt /remote/path  # upload a file

# SQLite
sqlite connect /path/to/db.sqlite
.tables          # list tables
select * from users;  # query
```

### Android-Specific

```bash
android root disable              # bypass Root detection
android sslpinning disable        # bypass SSL Pinning
android hooking list classes      # enumerate classes
android hooking list class_methods com.app.Main  # enumerate methods
android hooking watch class com.app.Main  # Hook all methods
android intent launch_activity com.app.MainActivity  # launch an Activity
android heap search instances com.app.User  # heap search
android keystore list             # Keystore entries
```

### iOS-Specific

```bash
ios jailbreak disable             # bypass jailbreak detection
ios sslpinning disable            # bypass SSL Pinning
ios keychain dump                 # export Keychain
ios nsuserdefaults get            # NSUserDefaults
ios nsurlcache dump               # HTTP cache
ios cookies get                   # read Cookies
ios pasteboard monitor            # monitor clipboard
ios ui dump                       # UI hierarchy
ios plist cat Info.plist          # read plist
```

## Root/Jailbreak-Free Deployment

### Android — Frida Gadget Injection

```bash
# 1. unpack the APK
apktool d app.apk -o app_unpacked

# 2. download frida-gadget and put it in the lib directory
cp frida-gadget-17.x.x-android-arm64.so \
   app_unpacked/lib/arm64-v8a/libfrida-gadget.so

# 3. inject System.loadLibrary("frida-gadget") into the smali
# modify the main Activity's onCreate or attachBaseContext

# 4. rebuild and sign
apktool b app_unpacked -o app_patched.apk
uber-apk-signer -a app_patched.apk

# 5. Objection automation
objection patchapk --source app.apk --skip-resources
```

### iOS — Frida Gadget Injection

```bash
# 1. decrypt the App Store IPA
python3 frida-ios-dump.py -u -p com.app.target

# 2. inject FridaGadget.dylib
# modify the Mach-O Load Commands, add @executable_path/FridaGadget.dylib

# 3. re-sign
codesign -f -s "Apple Development" Payload/App.app

# 4. install via Xcode sideload or AltStore
```

## Advanced SSL Pinning Bypass

### Multi-Layer Bypass (Android)

```javascript
// 1. OkHttp CertificatePinner
var CertificatePinner = Java.use("okhttp3.CertificatePinner");
CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function() {};

// 2. custom TrustManager
var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
TrustManagerImpl.verifyChain.implementation = function() { return []; };

// 3. WebView SSL Error
var SslErrorHandler = Java.use("android.webkit.SslErrorHandler");
SslErrorHandler.proceed.implementation = function() { return this.proceed(); };

// 4. Network Security Config
// requires modifying AndroidManifest.xml → android:networkSecurityConfig="@xml/network_security_config"
// add user certificate trust to the xml
```

### Multi-Layer Bypass (iOS)

```javascript
// 1. NSURLSession
var SecTrustEvaluate = Module.findExportByName("Security", "SecTrustEvaluate");
Interceptor.replace(SecTrustEvaluate, new NativeCallback(function(trust, result) {
    Memory.writeU32(result, 1); // kSecTrustResultProceed = 1
    return 0; // errSecSuccess
}, 'int', ['pointer', 'pointer']));

// 2. Alamofire
// Hook ServerTrustManager.evaluate → always return success
```

Source: Frida docs, Objection wiki, OWASP MSTG
