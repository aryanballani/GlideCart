package com.grocerybuddy.ui.components

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.grocerybuddy.network.RobotWebSocket
import com.grocerybuddy.ui.theme.*

@Composable
fun StatusCard(
    status: RobotWebSocket.RobotStatus,
    connectionState: RobotWebSocket.ConnectionState,
    modifier: Modifier = Modifier
) {
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseAlpha by infiniteTransition.animateFloat(
        initialValue = 0.3f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse"
    )

    val isConnected = connectionState == RobotWebSocket.ConnectionState.CONNECTED
    val targetLocked = status.targetLocked

    val backgroundGradient = when {
        !isConnected -> listOf(Color(0xFFEF4444), Color(0xFFDC2626))
        targetLocked -> listOf(Color(0xFF10B981), Color(0xFF059669))
        status.isTracking -> listOf(Color(0xFF3B82F6), Color(0xFF2563EB))
        else -> listOf(Color(0xFF64748B), Color(0xFF475569))
    }

    Card(
        modifier = modifier
            .fillMaxWidth()
            .height(180.dp),
        shape = RoundedCornerShape(24.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(
                    brush = Brush.horizontalGradient(
                        colors = backgroundGradient
                    )
                )
                .padding(24.dp)
        ) {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.SpaceBetween
            ) {
                // Top Section - Status
                Row(
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column {
                        Text(
                            text = when {
                                !isConnected -> "DISCONNECTED"
                                targetLocked -> "TARGET LOCKED"
                                status.isTracking -> "TRACKING..."
                                status.calibrated -> "READY"
                                else -> "STANDBY"
                            },
                            style = MaterialTheme.typography.headlineSmall,
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = when {
                                !isConnected -> "Waiting for connection"
                                targetLocked -> "Following target"
                                status.isTracking -> "Searching for target"
                                else -> "Press calibrate to start"
                            },
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color.White.copy(alpha = 0.9f)
                        )
                    }

                    // Animated Icon
                    Box(
                        modifier = Modifier
                            .size(56.dp)
                            .clip(RoundedCornerShape(16.dp))
                            .background(Color.White.copy(alpha = 0.2f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = when {
                                !isConnected -> Icons.Default.WifiOff
                                targetLocked -> Icons.Default.CheckCircle
                                status.isTracking -> Icons.Default.Search
                                else -> Icons.Default.Visibility
                            },
                            contentDescription = null,
                            tint = Color.White.copy(alpha = if (status.isTracking) pulseAlpha else 1f),
                            modifier = Modifier.size(32.dp)
                        )
                    }
                }

                // Bottom Section - Stats
                Row(
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    StatItem(
                        icon = Icons.Default.Speed,
                        label = "Distance",
                        value = if (isConnected) "${String.format("%.1f", status.distance)}m" else "--"
                    )
                    StatItem(
                        icon = Icons.Default.BatteryChargingFull,
                        label = "Battery",
                        value = if (isConnected) "${status.battery}%" else "--"
                    )
                    StatItem(
                        icon = if (status.obstacleDetected) Icons.Default.Warning else Icons.Default.CheckCircle,
                        label = "Obstacles",
                        value = if (isConnected) {
                            if (status.obstacleDetected) "Detected" else "Clear"
                        } else "--"
                    )
                }
            }
        }
    }
}

@Composable
private fun StatItem(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    label: String,
    value: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(Color.White.copy(alpha = 0.15f))
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = Color.White,
            modifier = Modifier.size(20.dp)
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            color = Color.White,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = Color.White.copy(alpha = 0.8f)
        )
    }
}
