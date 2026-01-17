# Add project specific ProGuard rules here.
-keep class com.grocerybuddy.** { *; }
-keepclassmembers class com.grocerybuddy.** { *; }

# OkHttp
-dontwarn okhttp3.**
-keep class okhttp3.** { *; }

# Room
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *
-dontwarn androidx.room.paging.**
