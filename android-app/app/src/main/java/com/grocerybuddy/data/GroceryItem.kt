package com.grocerybuddy.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "grocery_items")
data class GroceryItem(
    @PrimaryKey
    val name: String,
    val quantity: Int = 1,
    val removed: Boolean = false,
    val addedAt: Long = System.currentTimeMillis(),
    val removedAt: Long? = null
)
