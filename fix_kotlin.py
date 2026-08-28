
import os;

import base64

__min = '''
    package com.example.cybershield

    import android.Manifest
    import android.content.Intent
    import android.content.pm.PackageManager
    import android.os.Build
    import android.provider.Settings
    import androidx.core.app.ActivityCompat
    import androidx.core.content.ContextCompat
    import io.flutter.embedding.android.FlutterActivity
    import io.flutter.embedding.engine.FlutterEngine
    import io.flutter.plugin.common.EventChannel
    import io.flutter.plugin.common.MethodChannel

    class MainActivity : FlutterActivity() {
        companion object {
            private const val SMS_CHANNEL = "com.example.cybershield/sms"
            private const val PERMISSIONS_CHANNEL = "com.example.cybershield/permissions"
            private const val SMS_EVENT_CHANNEL = "com.example.cybershield/sms_stream"
            private var eventSink: EventChannel.EventSink? = null

            fun onSmsReceived(sender: String, message: String) {
                val data = HashMap<String, String>()
                data["sender"] = sender
                data["message"] = message
                eventSink?.success(data)
            }
        }

        override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
            super.configureFlutterEngine(flutterEngine)

            EventChannel(flutterEngine.dartExecutor.binaryMessenger, SMS_EVENT_CHANNEL).setStreamHandler(
                object : EventChannel.StreamHandler {
                    override fun onListen(arguments: Any?, events: EventChannel.EventSink?) {
                        eventSink = events
                    }

                    override fun onCancel(arguments: Any?) {
                        eventSink = null
                    }
                }
            )

            MethodChannel(flutterEngine.dartExecutor.binaryMessenger, SMS_CHANNEL).setMethodCallHandler { call, result ->
                if (call.method == "isListening") {
                    result.success(true)
                } else {
                    result.notImplemented()
                }
            }

            MethodChannel(flutterEngine.dartExecutor.binaryMessenger, PERMISSIONS_CHANNEL).setMethodCallHandler { call, result ->
                when (call.method) {
                    "requestAllPermissions" -> {
                        requestAppPermissions()
                        result.success(true)
                    }
                    "isNotificationAccessGranted" -> {
                        result.success(isNotificationServiceEnabled())
                    }
                    "openNotificationAccessSettings" -> {
                        val intent = Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS).apply {
                            flags = Intent.FLAG_ACTIVITY_NEW_TASK
                        }
                        startActivity(intent)
                        result.success(true)
                    }
                    else -> result.notImplemented()
                }
            }
        }

        private fun isNotificationServiceEnabled(): Boolean {
            val pkgName = packageName
            val flat = Settings.Secure.getString(contentResolver, "enabled_notification_listeners")
            return flat != null && flat.contains(pkgName)
        }

        private fun requestAppPermissions() {
            val permissions = mutableListOf(
                Manifest.permission.RECEIVE_SMS,
                Manifest.permission.READ_SMS,
                Manifest.permission.CAMERA
            )
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }

            val ungranted = permissions.filter {
                ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
            }

            if (ungranted.isNotEmpty()) {
                ActivityCompat.requestPermissions(this, ungranted.toTypedArray(), 101)
            }
        }
    }
'''

with open(r'C:\Users\hp\StudioProjects\cybershield\android\app\src\main\kotlin\com\example\cybershield\MainActivity.kt', 'w', encoding='utf-8') as f:
    f.write(__min.strip())

print('MainActivity.kt written!')
