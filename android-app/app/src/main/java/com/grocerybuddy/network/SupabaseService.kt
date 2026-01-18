package com.grocerybuddy.network

import com.grocerybuddy.BuildConfig
import com.grocerybuddy.data.GroceryItem
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject

class SupabaseService(
    private val baseUrl: String = BuildConfig.SUPABASE_URL,
    private val anonKey: String = BuildConfig.SUPABASE_ANON_KEY
) {
    private val client = OkHttpClient()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    private fun isConfigured(): Boolean = baseUrl.isNotBlank() && anonKey.isNotBlank()

    private fun requestBuilder(url: String): Request.Builder {
        return Request.Builder()
            .url(url)
            .addHeader("apikey", anonKey)
            .addHeader("Authorization", "Bearer $anonKey")
            .addHeader("Content-Type", "application/json")
    }

    suspend fun fetchItems(): List<GroceryItem> = withContext(Dispatchers.IO) {
        if (!isConfigured()) return@withContext emptyList()

        val url = "$baseUrl/rest/v1/grocery_items".toHttpUrl().newBuilder()
            .addQueryParameter("select", "name,quantity,removed,added_at,removed_at")
            .build()

        val request = requestBuilder(url.toString()).get().build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) return@withContext emptyList()
            val body = response.body?.string().orEmpty()
            val jsonArray = JSONArray(body)
            (0 until jsonArray.length()).mapNotNull { index ->
                val obj = jsonArray.optJSONObject(index) ?: return@mapNotNull null
                GroceryItem(
                    name = obj.optString("name"),
                    quantity = obj.optInt("quantity", 1),
                    removed = obj.optBoolean("removed", false),
                    addedAt = obj.optLong("added_at", System.currentTimeMillis()),
                    removedAt = if (obj.isNull("removed_at")) null else obj.optLong("removed_at")
                )
            }
        }
    }

    suspend fun upsertItem(item: GroceryItem) = withContext(Dispatchers.IO) {
        if (!isConfigured()) return@withContext

        val payload = JSONObject().apply {
            put("name", item.name)
            put("quantity", item.quantity)
            put("removed", item.removed)
            put("added_at", item.addedAt)
            if (item.removedAt != null) {
                put("removed_at", item.removedAt)
            } else {
                put("removed_at", JSONObject.NULL)
            }
        }

        val url = "$baseUrl/rest/v1/grocery_items".toHttpUrl().newBuilder()
            .addQueryParameter("on_conflict", "name")
            .build()

        val request = requestBuilder(url.toString())
            .addHeader("Prefer", "resolution=merge-duplicates")
            .post(payload.toString().toRequestBody(jsonMediaType))
            .build()

        client.newCall(request).execute().close()
    }

    suspend fun updateRemoved(name: String, removed: Boolean, removedAt: Long?) = withContext(Dispatchers.IO) {
        if (!isConfigured()) return@withContext

        val payload = JSONObject().apply {
            put("removed", removed)
            if (removedAt != null) {
                put("removed_at", removedAt)
            } else {
                put("removed_at", JSONObject.NULL)
            }
        }

        val url = "$baseUrl/rest/v1/grocery_items".toHttpUrl().newBuilder()
            .addQueryParameter("name", "eq.$name")
            .build()

        val request = requestBuilder(url.toString())
            .patch(payload.toString().toRequestBody(jsonMediaType))
            .build()

        client.newCall(request).execute().close()
    }

    suspend fun deleteItem(name: String) = withContext(Dispatchers.IO) {
        if (!isConfigured()) return@withContext

        val url = "$baseUrl/rest/v1/grocery_items".toHttpUrl().newBuilder()
            .addQueryParameter("name", "eq.$name")
            .build()

        val request = requestBuilder(url.toString()).delete().build()
        client.newCall(request).execute().close()
    }

    suspend fun deleteRemoved() = withContext(Dispatchers.IO) {
        if (!isConfigured()) return@withContext

        val url = "$baseUrl/rest/v1/grocery_items".toHttpUrl().newBuilder()
            .addQueryParameter("removed", "eq.true")
            .build()

        val request = requestBuilder(url.toString()).delete().build()
        client.newCall(request).execute().close()
    }

    suspend fun deleteAll() = withContext(Dispatchers.IO) {
        if (!isConfigured()) return@withContext

        val url = "$baseUrl/rest/v1/grocery_items".toHttpUrl().newBuilder()
            .addQueryParameter("name", "not.is.null")
            .build()

        val request = requestBuilder(url.toString()).delete().build()
        client.newCall(request).execute().close()
    }
}
