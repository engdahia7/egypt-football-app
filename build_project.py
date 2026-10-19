import os

def write_file(path, content):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ تم تحديث: {path}")

def update_fix():
    print("🚀 جاري إصلاح إذن الاتصال بالإنترنت وترويسات 365Scores...")

    # 1. تفعيل صلاحيات الإنترنت و cleartextTraffic في AndroidManifest
    write_file(".github/workflows/build_apk.yml", r'''
name: Build Compact APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - uses: subosito/flutter-action@v2
        with:
          channel: 'stable'

      - name: Create Android Platform
        run: flutter create --platforms=android --org com.egyptfootball.app .

      # تفعيل الإنترنت والسماح بمرور حركة البيانات عبر الشبكة
      - name: Add Internet Permission & App Name
        run: |
          sed -i 's/<application/<uses-permission android:name="android.permission.INTERNET"\/><uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"\/><application android:usesCleartextTraffic="true"/g' android/app/src/main/AndroidManifest.xml
          sed -i 's/android:label="[^"]*"/android:label="الكرة المصرية"/g' android/app/src/main/AndroidManifest.xml

      - name: Setup Custom App Icon
        run: |
          curl -sL "https://cdn-icons-png.flaticon.com/512/53/53283.png" -o icon.png
          for res in mipmap-mdpi mipmap-hdpi mipmap-xhdpi mipmap-xxhdpi mipmap-xxxhdpi; do
            mkdir -p android/app/src/main/res/$res
            cp icon.png android/app/src/main/res/$res/ic_launcher.png
          done

      - name: Get Dependencies
        run: flutter pub get

      - name: Build Optimized Split APK
        run: flutter build apk --release --split-per-abi

      - name: Upload Compact APK
        uses: actions/upload-artifact@v4
        with:
          name: Egyptian-Football-App-Fix
          path: build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
''')

    # 2. تحسين كود جلب البيانات وإضافة ترويسات متصفح كاملة لمنع الحظر
    write_file("lib/core/smart_api_cache.dart", r'''
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class SmartApiCache {
  static Future<Map<String, dynamic>> get({
    required String cacheKey,
    required String url,
    required Duration ttl,
    bool forceRefresh = false,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final String? cachedJson = prefs.getString('365_data_$cacheKey');
    final int? cachedTime = prefs.getInt('365_time_$cacheKey');
    final int now = DateTime.now().millisecondsSinceEpoch;

    if (!forceRefresh && cachedJson != null && cachedTime != null) {
      final int ageInMinutes = ((now - cachedTime) / 60000).round();
      if (ageInMinutes < ttl.inMinutes) {
        return json.decode(cachedJson);
      }
    }

    try {
      final response = await http.get(
        Uri.parse(url),
        headers: {
          'User-Agent':
              'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
          'Accept': 'application/json, text/plain, */*',
          'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
          'Referer': 'https://www.365scores.com/',
          'Origin': 'https://www.365scores.com',
        },
      ).timeout(const Duration(seconds: 12));

      if (response.statusCode == 200) {
        final String bodyText = utf8.decode(response.bodyBytes);
        final Map<String, dynamic> data = json.decode(bodyText);
        await prefs.setString('365_data_$cacheKey', bodyText);
        await prefs.setInt('365_time_$cacheKey', now);
        return data;
      } else {
        throw Exception('Status code: ${response.statusCode}');
      }
    } catch (e) {
      if (cachedJson != null) {
        return json.decode(cachedJson);
      }
      rethrow;
    }
  }
}
''')

    print("\n🎉 تم تحديث الإعدادات وترويسات الاتصال بنجاح!");

if __name__ == "__main__":
    update_fix()