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
