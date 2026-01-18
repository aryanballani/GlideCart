package com.grocerybuddy.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.grocerybuddy.data.GroceryDatabase
import com.grocerybuddy.data.GroceryItem
import com.grocerybuddy.network.RobotWebSocket
import com.grocerybuddy.network.SupabaseService
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class RobotViewModel(application: Application) : AndroidViewModel(application) {

    private val database = GroceryDatabase.getDatabase(application)
    private val groceryDao = database.groceryDao()

    private val robotWebSocket = RobotWebSocket()
    private val supabaseService = SupabaseService()

    val connectionState = robotWebSocket.connectionState.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        RobotWebSocket.ConnectionState.DISCONNECTED
    )

    val robotStatus = robotWebSocket.robotStatus.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        RobotWebSocket.RobotStatus()
    )

    val videoFrame = robotWebSocket.videoFrame.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        null
    )

    val groceryList = groceryDao.getAllItems().stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        emptyList()
    )

    private val _showCalibrationSuccess = MutableStateFlow(false)
    val showCalibrationSuccess = _showCalibrationSuccess.asStateFlow()

    private val _showEmergencyStopAlert = MutableStateFlow(false)
    val showEmergencyStopAlert = _showEmergencyStopAlert.asStateFlow()

    private val _serverIp = MutableStateFlow("10.19.129.238")
    val serverIp = _serverIp.asStateFlow()

    init {
        connectToRobot()
        syncFromSupabase()
        observeDetectedObjects()
    }

    // Robot Control Functions
    fun connectToRobot(ip: String = _serverIp.value) {
        _serverIp.value = ip
        robotWebSocket.connect(ip, 8765)
    }

    fun disconnectFromRobot() {
        robotWebSocket.disconnect()
    }

    fun reconnect(ip: String = _serverIp.value) {
        _serverIp.value = ip
        robotWebSocket.reconnect(ip, 8765)
    }

    fun updateServerIp(ip: String) {
        _serverIp.value = ip
    }

    fun calibrate() {
        robotWebSocket.calibrate()
        _showCalibrationSuccess.value = true
        viewModelScope.launch {
            kotlinx.coroutines.delay(2000)
            _showCalibrationSuccess.value = false
        }
    }

    fun startTracking() {
        robotWebSocket.startTracking()
    }

    fun stopTracking() {
        robotWebSocket.stopTracking()
    }

    fun emergencyStop() {
        robotWebSocket.emergencyStop()
        _showEmergencyStopAlert.value = true
        viewModelScope.launch {
            kotlinx.coroutines.delay(3000)
            _showEmergencyStopAlert.value = false
        }
    }

    fun setMode(mode: RobotWebSocket.CameraMode) {
        robotWebSocket.setMode(mode)
    }

    // Grocery List Functions
    fun addGroceryItem(name: String, quantity: Int = 1) {
        viewModelScope.launch {
            if (name.isNotBlank()) {
                val item = GroceryItem(
                    name = name.trim(),
                    quantity = quantity.coerceAtLeast(1),
                    removed = false,
                    addedAt = System.currentTimeMillis(),
                    removedAt = null
                )
                groceryDao.insert(item)
                supabaseService.upsertItem(item)
            }
        }
    }

    fun toggleItem(item: GroceryItem) {
        viewModelScope.launch {
            val willRemove = !item.removed
            val updated = item.copy(
                removed = willRemove,
                removedAt = if (willRemove) System.currentTimeMillis() else null
            )
            groceryDao.update(updated)
            supabaseService.updateRemoved(updated.name, updated.removed, updated.removedAt)
        }
    }

    fun deleteItem(item: GroceryItem) {
        viewModelScope.launch {
            groceryDao.delete(item)
            supabaseService.deleteItem(item.name)
        }
    }

    fun deleteCheckedItems() {
        viewModelScope.launch {
            groceryDao.deleteRemovedItems()
            supabaseService.deleteRemoved()
        }
    }

    fun clearAllItems() {
        viewModelScope.launch {
            groceryDao.deleteAll()
            supabaseService.deleteAll()
        }
    }

    private fun syncFromSupabase() {
        viewModelScope.launch {
            val remoteItems = supabaseService.fetchItems()
            remoteItems.forEach { groceryDao.insert(it) }
        }
    }

    private fun observeDetectedObjects() {
        viewModelScope.launch {
            robotWebSocket.robotStatus
                .map { it.detectedObject.trim() }
                .filter { it.isNotBlank() }
                .distinctUntilChanged()
                .collect { detected ->
                    // Check if item exists in list
                    val match = groceryList.value.firstOrNull {
                        it.name.equals(detected, ignoreCase = true)
                    }

                    if (match != null) {
                        // Item exists - strike it off if not already removed
                        if (!match.removed) {
                            val updated = match.copy(
                                removed = true,
                                removedAt = System.currentTimeMillis()
                            )
                            groceryDao.update(updated)
                            supabaseService.updateRemoved(updated.name, true, updated.removedAt)
                        }
                    } else {
                        // Item not on list - add it and strike it off immediately
                        val newItem = GroceryItem(
                            name = detected,
                            quantity = 1,
                            removed = true,
                            addedAt = System.currentTimeMillis(),
                            removedAt = System.currentTimeMillis()
                        )
                        groceryDao.insert(newItem)
                        supabaseService.upsertItem(newItem)
                    }
                }
        }
    }

    override fun onCleared() {
        super.onCleared()
        robotWebSocket.disconnect()
    }
}
