import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class FavoriteTeam {
  final String name;
  final String logo;

  FavoriteTeam({required this.name, required this.logo});

  Map<String, dynamic> toJson() => {'name': name, 'logo': logo};

  factory FavoriteTeam.fromJson(Map<String, dynamic> json) => FavoriteTeam(
        name: json['name'] ?? 'الأهلي',
        logo: json['logo'] ?? '',
      );
}

class FavoriteTeamManager {
  static const String _key = 'fav_team_365_pref';

  static Future<void> saveFavorite(FavoriteTeam team) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_key, json.encode(team.toJson()));
  }

  static Future<FavoriteTeam?> getFavorite() async {
    final prefs = await SharedPreferences.getInstance();
    final String? jsonStr = prefs.getString(_key);
    if (jsonStr == null) return null;
    return FavoriteTeam.fromJson(json.decode(jsonStr));
  }
}
