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
    final String? cachedJson = prefs.getString('cache_365_$cacheKey');
    final int? cachedTime = prefs.getInt('time_365_$cacheKey');
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
          'Accept': 'application/json',
          'User-Agent': '365Scores-Android/12.4.0',
        },
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final String bodyText = utf8.decode(response.bodyBytes);
        final Map<String, dynamic> data = json.decode(bodyText);
        await prefs.setString('cache_365_$cacheKey', bodyText);
        await prefs.setInt('time_365_$cacheKey', now);
        return data;
      } else {
        throw Exception('رمز الاستجابة: ${response.statusCode}');
      }
    } catch (e) {
      if (cachedJson != null) {
        return json.decode(cachedJson);
      }
      rethrow;
    }
  }
}
