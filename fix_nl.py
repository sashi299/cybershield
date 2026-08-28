
import os;

ynl = '''
    package com.example.cybershield

    import android.app.Notification
    import android.app.NotificationChannel
    import android.app.NotificationManager
    import android.app.PendingIntent
    import android.content.Context
    import android.content.Intent
    import android.os.Build
    import android.service.notification.NotificationListenerService
    import android.service.notification.StatusBarNotification
    import android.util.Log
    import org.json.JSONObject
    import java.io.OutputStreamWriter
    import java.net.HttpURLConnection
    import java.net.URL

    class CyberShieldNotificationListener : NotificationListenerService() {
        companion object {
            const val CHANNEL_ID = "cybershield_threat_alerts"
            const val CHANNEL_NAME = "CyberShield Security Alerts"
            const val BACKEND_URL = "http://10.10.83.190:8000/api/analyze/text"

            val MONITORED_PACKAGES = setOf(
                "com.whatsapp",
                "com.whatsapp.w4b",
                "org.telegram.messenger",
                "com.google.android.apps.messaging",
                "com.samsung.android.messaging",
                "com.instagram.android",
                "com.google.android.gm"
            )
        }

        override fun onNotificationPosted(sbn: StatusBarNotification?) {
            super.onNotificationPosted(sbn)
            if (sbn == null) return

            val packageName = sbn.packageName ?: return
            if (packageName == applicationContext.packageName) return

            if (MONITORED_OACKAGES.contains(packageName) || packageName.contains("whatsapp") || packageName.contains("messaging") || packageName.contains("telegram")) {
                val notification = sbn.notification ?: return
                val extras = notification.extras ?: return

                val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString() ?: ""
                val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString() ?: ""
                val bigText = extras.getCharSequence(Notification.EXTRA_BIG_TEXT)?.toString() ?: ""
                val messageBody = if (bigText.isNotEmpty()) bigText else text

                if (messageBody.isEmpty() || messageBody.contains("Checking for new messages") || messageBody.contains("WhatsApp Web")) {
                    return
                }

                val appName = when {
                    packageName.contains("whatsapp") -> "WhatsApp"
                    packageName.contains("telegram") -> "Telegram"
                    packageName.contains("messaging") -> "SMS"
                    packageName.contains("instagram") -> "Instagram"
                    packageName.contains("gm") -> "GMail"
                    else -> "Message"
                }

                val sender = if (title.isNotEmpty()) title else appName
                Log.d("CyberShieldWatcher", "Incoming " + appName + " from " + sender + ": " + messageBody)

                MainActivity.onSmsReceived(sender, messageBody)

                Thread {
                    analyzeAndNotify(applicationContext, appName, sender, messageBody)
                }.start()
            }
        }

        private fun analyzeAndNotify(context: Context, appName: String, sender: String, message: String) {
            try {
                val url = URL(BACKEND_URL)
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json; utf-8")
                conn.setRequestProperty("Accept", "application/json")
                conn.doOutput = true
                conn.connectTimeout = 4000
                conn.readTimeout = 4000

                val jsonInput = JSONObject()
                jsonInput.put("text", message)
                jsonInput.put("type", "sms")

                OutputStreamWriter(conn.outputStream).use { writer ->
                    writer.write(jsonInput.toString())
                    writer.flush()
                }

                if (conn.responseCode == 200) {
                    val responseText = conn.inputStream.bufferedReader().use { it.readText() }
                    val resultJson = JSONObject(responseText)
                    val verdict = resultJson.optString("verdict", "Safe")
                    val confidence = resultJson.optDouble("confidence", 0.0)
                    val explanation = resultJson.optString("explanation", "")

                    if (verdict.equals("Dangerous", ignoreCase = true) || verdict.equals("Suspicious", ignoreCase = true)) {
                        showSystemThreatNotification(context, appName, sender, message, verdict, confidence, explanation)
                    }
                }
            } catch (e: Exception) {
                Log.e("CyberShieldWatcher", "Background analysis error: " + e.message)
            }
        }


        private fun showSystemThreatNotification(
            context: Context,
            appName: String,
            sender: String,
            message: String,
            verdict: String,
            confidence: Double,
            explanation: String
        ) {
            val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val channel = NotificationChannel(
                    CHANNEL_ID,
                    CHANNEL_NAME,
                    NotificationManager.IMPORTANCE_HIGH
                ).apply {
                    description = "High priority phishing and fraud alerts"
                    enableVibration(true)
                    vibrationPattern = longArrayOf(0, 500, 200, 500)
                }
                notificationManager.createNotificationChannel(channel)
            }


            val launchIntent = Intent(context, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                putExtra("sender", sender)
                putExtra("message", message)
                putExtra("verdict", verdict)
                putExtra("appName", appName)
            }

            val pendingIntent = PendingIntent.getActivity(
                context,
                System.currentTimeMillis().toInt(),
                launchIntent,
                if (Build.VERSION_CODES.M <= Build.VERSION.SDK_INT) PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT else PendingIntent.FLAG_UPDATE_CURRENT
            )

            val isDangerous = verdict.equals("Dangerous", ignoreCase = true)
            val title = if (isDangerous) "[PHISHING ALERT] " + appName + ": " + sender else "[USPICIOUS LINK] " + appName + ": " + sender
            val content = verdict + " threat detected: " + explanation

            val builder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                Notification.Builder(context, CHANNEL_ID)
            } else {
                @Suppress["DEPRECATION"]
                Notification.Builder(context)
            }

            val notification = builder
                .setSmallIcon(android.R.drawable.ic_dialog_alert)
                .setContentTitle(title)
                .setContentText(content)
                .setStyle(Notification.BigTextStyle().bigText("App: " + appName + "\nFrom: " + sender + "\n\nMessage: " + message + "\n\nVerdict: " + verdict + " (" + confidence.toString() + "%)\n" + explanation))
                .setAutoCancel(true)
                .setContentIntent(pendingIntent)
                .build()

            notificationManager.notify(System.currentTimeMillis().toInt(), notification)
        }
    }
'''

with open(r'C:\Users\hp\StudioProjects\cybershield\android\app\src\main\kotlin\com\example\cybershield\CyberShieldNotificationListener.kt', 'w', encoding='utf-8') as f:
    f.write(ynl.strip())

print('CyberShieldNotificationListener.kt written!')
