package com.grocerybuddy.data

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface GroceryDao {
    @Query("SELECT * FROM grocery_items ORDER BY addedAt DESC")
    fun getAllItems(): Flow<List<GroceryItem>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: GroceryItem)

    @Update
    suspend fun update(item: GroceryItem)

    @Delete
    suspend fun delete(item: GroceryItem)

    @Query("DELETE FROM grocery_items WHERE name = :name")
    suspend fun deleteByName(name: String)

    @Query("DELETE FROM grocery_items WHERE removed = 1")
    suspend fun deleteRemovedItems()

    @Query("DELETE FROM grocery_items")
    suspend fun deleteAll()
}
