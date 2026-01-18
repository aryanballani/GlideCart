package com.grocerybuddy.network

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import okhttp3.*
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class RobotWebSocket {

    private val client = OkHttpClient.Builder()
        .pingInterval(30, TimeUnit.SECONDS)
        .retryOnConnectionFailure(true)
        .build()

    private var webSocket: WebSocket? = null
    private var currentServerUrl: String = "ws://10.19.129.238:8765"

    private val _connectionState = MutableStateFlow(ConnectionState.DISCONNECTED)
    val connectionState: StateFlow<ConnectionState> = _connectionState.asStateFlow()

    private val _robotStatus = MutableStateFlow(RobotStatus())
    val robotStatus: StateFlow<RobotStatus> = _robotStatus.asStateFlow()

    private val _videoFrame = MutableStateFlow<String?>(null)
    val videoFrame: StateFlow<String?> = _videoFrame.asStateFlow()

    enum class ConnectionState {
        DISCONNECTED,
        CONNECTING,
        CONNECTED,
        ERROR
    }

    enum class CameraMode {
        FOLLOW, SCAN
    }

    data class RobotStatus(
        val isTracking: Boolean = false,
        val distance: Float = 0f,
        val battery: Int = 100,
        val targetLocked: Boolean = false,
        val obstacleDetected: Boolean = false,
        val calibrated: Boolean = false,
        val mode: CameraMode = CameraMode.SCAN,
        val detectedObject: String = ""
    )

    fun connect(serverIp: String = "10.19.129.238", serverPort: Int = 8765) {
        if (_connectionState.value == ConnectionState.CONNECTED) {
            return
        }

        currentServerUrl = "ws://$serverIp:$serverPort"
        _connectionState.value = ConnectionState.CONNECTING

        val request = Request.Builder()
            .url(currentServerUrl)
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                _connectionState.value = ConnectionState.CONNECTED
                // Request video stream on connection
                sendCommand("start_video_stream")
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val json = JSONObject(text)
                    val type = json.optString("type", "status")

                    when (type) {
                        "status" -> {
                            val modeStr = json.optString("mode", "scan")
                            val mode = if (modeStr == "follow") CameraMode.FOLLOW else CameraMode.SCAN

                            _robotStatus.value = RobotStatus(
                                isTracking = json.optBoolean("tracking", false),
                                distance = json.optDouble("distance", 0.0).toFloat(),
                                battery = json.optInt("battery", 100),
                                targetLocked = json.optBoolean("target_locked", false),
                                obstacleDetected = json.optBoolean("obstacle_detected", false),
                                calibrated = json.optBoolean("calibrated", false),
                                mode = mode,
                                detectedObject = json.optString("detected_object", "")
                            )
                        }
                        "video_frame" -> {
                            val frameData = json.optString("frame", "")
                            if (frameData.isNotEmpty()) {
                                _videoFrame.value = frameData
                            }
                        }
                    }
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                _connectionState.value = ConnectionState.DISCONNECTED
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _connectionState.value = ConnectionState.ERROR
                t.printStackTrace()
            }
        })
    }

    private fun sendCommand(command: String, extras: Map<String, Any> = emptyMap()) {
        try {
            val json = JSONObject().apply {
                put("command", command)
                put("timestamp", System.currentTimeMillis())
                extras.forEach { (key, value) -> put(key, value) }
            }
            webSocket?.send(json.toString())
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun calibrate() = sendCommand("calibrate")

    fun startTracking() = sendCommand("start_tracking")

    fun stopTracking() = sendCommand("stop_tracking")

    fun emergencyStop() = sendCommand("emergency_stop")

    fun requestStatus() = sendCommand("get_status")

    fun setMode(mode: CameraMode) {
        val modeStr = if (mode == CameraMode.FOLLOW) "follow" else "scan"
        sendCommand("set_mode", mapOf("mode" to modeStr))
    }

    fun disconnect() {
        webSocket?.close(1000, "User disconnected")
        _connectionState.value = ConnectionState.DISCONNECTED
    }

    fun reconnect(serverIp: String = "10.19.129.238", serverPort: Int = 8765) {
        disconnect()
        connect(serverIp, serverPort)
    }

    fun getCurrentServerUrl(): String = currentServerUrl
}
