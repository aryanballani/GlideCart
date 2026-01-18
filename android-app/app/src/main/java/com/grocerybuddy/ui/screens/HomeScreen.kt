package com.grocerybuddy.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.grocerybuddy.network.RobotWebSocket
import com.grocerybuddy.ui.components.*
import com.grocerybuddy.ui.theme.*
import com.grocerybuddy.viewmodel.RobotViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(viewModel: RobotViewModel) {
    val connectionState by viewModel.connectionState.collectAsState()
    val robotStatus by viewModel.robotStatus.collectAsState()
    val groceryList by viewModel.groceryList.collectAsState()
    val showCalibrationSuccess by viewModel.showCalibrationSuccess.collectAsState()
    val showEmergencyStopAlert by viewModel.showEmergencyStopAlert.collectAsState()
    val videoFrame by viewModel.videoFrame.collectAsState()
    val serverIp by viewModel.serverIp.collectAsState()

    var newItemText by remember { mutableStateOf("") }
    var newItemQuantity by remember { mutableStateOf("1") }
    var showAddItemDialog by remember { mutableStateOf(false) }
    var showSettingsDialog by remember { mutableStateOf(false) }
    var showVideoFeed by remember { mutableStateOf(false) }

    val isConnected = connectionState == RobotWebSocket.ConnectionState.CONNECTED

    Box(modifier = Modifier.fillMaxSize()) {
        Scaffold(
            topBar = {
                TopAppBar(
                    title = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text(
                                "Grocery Buddy",
                                style = MaterialTheme.typography.headlineSmall,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    },
                    actions = {
                        // Connection Status Indicator
                        AnimatedConnectionIndicator(connectionState)

                        // Video feed toggle
                        IconButton(onClick = { showVideoFeed = !showVideoFeed }) {
                            Icon(
                                imageVector = if (showVideoFeed) Icons.Default.Videocam else Icons.Default.VideocamOff,
                                contentDescription = "Toggle video feed",
                                tint = if (showVideoFeed) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                            )
                        }

                        // Settings button
                        IconButton(onClick = { showSettingsDialog = true }) {
                            Icon(
                                imageVector = Icons.Default.Settings,
                                contentDescription = "Settings",
                                tint = MaterialTheme.colorScheme.onSurface
                            )
                        }

                        // Reconnect button
                        IconButton(onClick = { viewModel.reconnect() }) {
                            Icon(
                                imageVector = Icons.Default.Refresh,
                                contentDescription = "Reconnect",
                                tint = MaterialTheme.colorScheme.onSurface
                            )
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.surface
                    )
                )
            },
            floatingActionButton = {
                ExtendedFloatingActionButton(
                    onClick = { showAddItemDialog = true },
                    icon = {
                        Icon(
                            imageVector = Icons.Default.Add,
                            contentDescription = "Add item"
                        )
                    },
                    text = { Text("Add Item") },
                    containerColor = Primary,
                    contentColor = Color.White
                )
            }
        ) { padding ->
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
                contentPadding = PaddingValues(vertical = 16.dp)
            ) {
                // Status Card
                item {
                    StatusCard(
                        status = robotStatus,
                        connectionState = connectionState
                    )
                }

                // Video Feed (if enabled)
                if (showVideoFeed && videoFrame != null) {
                    item {
                        VideoFeedCard(videoFrame = videoFrame!!)
                    }
                }

                // Control Buttons
                item {
                    ControlButtons(
                        isTracking = robotStatus.isTracking,
                        isConnected = isConnected,
                        currentMode = robotStatus.mode.name.lowercase(),
                        onCalibrate = { viewModel.calibrate() },
                        onStartStop = {
                            if (robotStatus.isTracking) {
                                viewModel.stopTracking()
                            } else {
                                viewModel.startTracking()
                            }
                        },
                        onEmergencyStop = { viewModel.emergencyStop() },
                        onModeChange = { mode ->
                            val cameraMode = if (mode == "follow") {
                                RobotWebSocket.CameraMode.FOLLOW
                            } else {
                                RobotWebSocket.CameraMode.SCAN
                            }
                            viewModel.setMode(cameraMode)
                        }
                    )
                }

                // Grocery List Section Header
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Shopping List",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface
                        )

                        if (groceryList.isNotEmpty()) {
                            TextButton(onClick = { viewModel.deleteCheckedItems() }) {
                                Text("Clear Removed")
                            }
                        }
                    }
                }

                // Grocery List Items
                if (groceryList.isEmpty()) {
                    item {
                        EmptyListPlaceholder()
                    }
                } else {
                    items(
                        items = groceryList,
                            key = { it.name }
                    ) { item ->
                        AnimatedVisibility(
                            visible = true,
                            enter = fadeIn() + slideInVertically(),
                            exit = fadeOut() + slideOutVertically()
                        ) {
                            GroceryItemCard(
                                item = item,
                                onToggle = { viewModel.toggleItem(item) },
                                onDelete = { viewModel.deleteItem(item) }
                            )
                        }
                    }
                }

                // Bottom spacing for FAB
                item {
                    Spacer(modifier = Modifier.height(80.dp))
                }
            }
        }

        // Snackbar notifications
        AnimatedVisibility(
            visible = showCalibrationSuccess,
            enter = slideInVertically(initialOffsetY = { -it }) + fadeIn(),
            exit = slideOutVertically(targetOffsetY = { -it }) + fadeOut(),
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(top = 80.dp)
        ) {
            SuccessSnackbar(message = "Calibration successful!")
        }

        AnimatedVisibility(
            visible = showEmergencyStopAlert,
            enter = slideInVertically(initialOffsetY = { -it }) + fadeIn(),
            exit = slideOutVertically(targetOffsetY = { -it }) + fadeOut(),
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(top = 80.dp)
        ) {
            ErrorSnackbar(message = "Emergency stop activated!")
        }
    }

    // Add Item Dialog
    if (showAddItemDialog) {
        AlertDialog(
            onDismissRequest = {
                showAddItemDialog = false
                newItemText = ""
                newItemQuantity = "1"
            },
            title = {
                Text(
                    "Add Grocery Item",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedTextField(
                        value = newItemText,
                        onValueChange = { newItemText = it },
                        placeholder = { Text("Enter item name") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp)
                    )
                    OutlinedTextField(
                        value = newItemQuantity,
                        onValueChange = { newItemQuantity = it.filter { ch -> ch.isDigit() } },
                        placeholder = { Text("Quantity") },
                        singleLine = true,
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp)
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (newItemText.isNotBlank()) {
                            val quantity = newItemQuantity.toIntOrNull() ?: 1
                            viewModel.addGroceryItem(newItemText, quantity)
                            newItemText = ""
                            newItemQuantity = "1"
                            showAddItemDialog = false
                        }
                    },
                    enabled = newItemText.isNotBlank()
                ) {
                    Text("Add")
                }
            },
            dismissButton = {
                TextButton(onClick = {
                    showAddItemDialog = false
                    newItemText = ""
                    newItemQuantity = "1"
                }) {
                    Text("Cancel")
                }
            }
        )
    }

    // Settings Dialog
    if (showSettingsDialog) {
        var ipText by remember { mutableStateOf(serverIp) }

        AlertDialog(
            onDismissRequest = { showSettingsDialog = false },
            icon = {
                Icon(
                    imageVector = Icons.Default.Settings,
                    contentDescription = null
                )
            },
            title = {
                Text("Robot Settings")
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "Raspberry Pi IP Address",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    OutlinedTextField(
                        value = ipText,
                        onValueChange = { ipText = it },
                        placeholder = { Text("10.19.129.238") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp)
                    )
                    Text(
                        text = "Enter the IP address of your Raspberry Pi. Default port 8765 will be used.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.updateServerIp(ipText)
                        viewModel.reconnect(ipText)
                        showSettingsDialog = false
                    }
                ) {
                    Text("Save & Reconnect")
                }
            },
            dismissButton = {
                TextButton(onClick = { showSettingsDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Composable
private fun VideoFeedCard(videoFrame: String) {
    val bitmap = remember(videoFrame) {
        try {
            val imageBytes = android.util.Base64.decode(videoFrame, android.util.Base64.DEFAULT)
            android.graphics.BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
        } catch (e: Exception) {
            null
        }
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(240.dp),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            if (bitmap != null) {
                androidx.compose.foundation.Image(
                    bitmap = bitmap.asImageBitmap(),
                    contentDescription = "Live camera feed",
                    modifier = Modifier.fillMaxSize(),
                    contentScale = androidx.compose.ui.layout.ContentScale.Fit
                )
            } else {
                Text(
                    text = "Loading video...",
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun AnimatedConnectionIndicator(connectionState: RobotWebSocket.ConnectionState) {
    val infiniteTransition = rememberInfiniteTransition(label = "connection")
    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000),
            repeatMode = RepeatMode.Reverse
        ),
        label = "alpha"
    )

    val (icon, color, contentAlpha) = when (connectionState) {
        RobotWebSocket.ConnectionState.CONNECTED -> Triple(Icons.Default.Wifi, Success, 1f)
        RobotWebSocket.ConnectionState.CONNECTING -> Triple(Icons.Default.WifiFind, Warning, alpha)
        RobotWebSocket.ConnectionState.ERROR -> Triple(Icons.Default.WifiOff, Error, 1f)
        RobotWebSocket.ConnectionState.DISCONNECTED -> Triple(Icons.Default.WifiOff, Color.Gray, 1f)
    }

    Icon(
        imageVector = icon,
        contentDescription = "Connection Status",
        tint = color.copy(alpha = contentAlpha),
        modifier = Modifier
            .padding(end = 8.dp)
            .size(24.dp)
    )
}

@Composable
private fun EmptyListPlaceholder() {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(120.dp),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.ShoppingCart,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
                modifier = Modifier.size(48.dp)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "No items yet",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
            )
            Text(
                text = "Tap + to add items to your list",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
        }
    }
}

@Composable
private fun SuccessSnackbar(message: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth(0.9f)
            .padding(horizontal = 16.dp),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Success)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.CheckCircle,
                contentDescription = null,
                tint = Color.White,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Text(
                text = message,
                color = Color.White,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium
            )
        }
    }
}

@Composable
private fun ErrorSnackbar(message: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth(0.9f)
            .padding(horizontal = 16.dp),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Error)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Warning,
                contentDescription = null,
                tint = Color.White,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Text(
                text = message,
                color = Color.White,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium
            )
        }
    }
}
