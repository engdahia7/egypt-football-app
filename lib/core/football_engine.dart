import 'dart:convert';
import 'package:http/http.dart' as http;

class FootballEngine {
  static const Map<String, String> teamLogos = {
    "الأهلي": "https://upload.wikimedia.org/wikipedia/ar/8/8c/Al_Ahly_SC_logo.png",
    "الزمالك": "https://upload.wikimedia.org/wikipedia/ar/0/04/ZamalekSC.png",
    "بيراميدز": "https://upload.wikimedia.org/wikipedia/ar/c/ce/Pyramids_FC_logo.png",
    "المصري": "https://upload.wikimedia.org/wikipedia/ar/f/fa/Al-Masry_SC_Logo.png",
    "المصري البورسعيدي": "https://upload.wikimedia.org/wikipedia/ar/f/fa/Al-Masry_SC_Logo.png",
    "الاتحاد السكندري": "https://upload.wikimedia.org/wikipedia/ar/4/4c/Al_Ittihad_Alexandria_Club_logo.png",
    "الإسماعيلي": "https://upload.wikimedia.org/wikipedia/ar/0/0c/Ismaily_SC_logo.png",
    "زد إف سي": "https://upload.wikimedia.org/wikipedia/ar/4/4b/ZED_FC_logo.png",
    "سيراميكا كليوباترا": "https://upload.wikimedia.org/wikipedia/ar/c/cf/Ceramica_Cleopatra_FC_Logo.png",
    "سموحة": "https://upload.wikimedia.org/wikipedia/ar/8/87/Smouha_SC_Logo.png",
    "طلائع الجيش": "https://upload.wikimedia.org/wikipedia/ar/5/5a/Tala%27ea_El_Gaish_SC_logo.png",
    "إنبي": "https://upload.wikimedia.org/wikipedia/ar/7/75/ENPPI_Club_logo.png",
    "مودرن سبورت": "https://upload.wikimedia.org/wikipedia/ar/0/00/Modern_Sport_FC_logo.png",
    "غزل المحلة": "https://upload.wikimedia.org/wikipedia/ar/3/36/Ghazl_El_Mahalla_SC_logo.png",
    "فاركو": "https://upload.wikimedia.org/wikipedia/ar/9/98/Pharco_FC_logo.png",
    "الجونة": "https://upload.wikimedia.org/wikipedia/ar/2/23/El_Gouna_FC_logo.png",
    "البنك الأهلي": "https://upload.wikimedia.org/wikipedia/ar/2/2f/National_Bank_of_Egypt_SC_logo.png",
    "حرس الحدود": "https://upload.wikimedia.org/wikipedia/ar/0/09/Haras_El_Hodood_SC_logo.png",
    "بتروجيت": "https://upload.wikimedia.org/wikipedia/ar/8/81/Petrojet_SC_logo.png",
  };

  static String getLogo(String teamName) {
    for (var key in teamLogos.keys) {
      if (teamName.contains(key) || key.contains(teamName)) {
        return teamLogos[key]!;
      }
    }
    return "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/26bd.png";
  }

  // 1. جلب مباريات اليوم الحقيقية مباشرة
  static Future<List<Map<String, dynamic>>> getMatches(String dateStr) async {
    final cleanDate = dateStr.replaceAll("-", "");
    final url = 'https://www.fotmob.com/api/matches?date=$cleanDate&timezone=Africa%2FCairo';

    try {
      final response = await http.get(
        Uri.parse(url),
        headers: {
          'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36',
          'Accept': 'application/json',
        },
      ).timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final List<dynamic> leagues = data['leagues'] ?? [];
        List<Map<String, dynamic>> results = [];

        for (var lg in leagues) {
          final String leagueName = lg['name'] ?? '';
          final String country = lg['ccode'] ?? '';
          
          // حصر المباريات في بطولات مصر أو الأندية المصرية في البطولات القارية
          final bool isEgypt = country == 'EGY' || 
                               leagueName.contains('Egypt') || 
                               leagueName.contains('الدوري المصري') ||
                               leagueName.contains('كأس مصر') ||
                               leagueName.contains('CAF');

          if (isEgypt) {
            for (var m in (lg['matches'] ?? [])) {
              final homeName = m['home']['name'] ?? '';
              final awayName = m['away']['name'] ?? '';
              final status = m['status'] ?? {};
              final bool started = status['started'] ?? false;
              final bool finished = status['finished'] ?? false;

              String statusText = 'لم تبدأ';
              if (finished) {
                statusText = 'انتهت';
              } else if (started) {
                statusText = 'مباشر ${status['liveTime']?['short'] ?? ''}';
              }

              results.add({
                "id": m['id'],
                "league": leagueName,
                "home": homeName,
                "away": awayName,
                "home_logo": getLogo(homeName),
                "away_logo": getLogo(awayName),
                "time": status['startTimeStr'] ?? '20:00',
                "date": dateStr,
                "status": statusText,
                "home_score": started ? m['home']['score'] : null,
                "away_score": started ? m['away']['score'] : null,
                "tv": "أون تايم سبورتس HD"
              });
            }
          }
        }
        return results;
      }
    } catch (_) {}
    return [];
  }

  // 2. جلب جدول ترتيب الدوري المصري الفعلي مباشرة
  static Future<List<Map<String, dynamic>>> getStandings() async {
    // كود الدوري المصري في واجهة البطولات هو 322
    const url = 'https://www.fotmob.com/api/leagues?id=322&tab=table&type=league&timeZone=Africa%2FCairo';

    try {
      final response = await http.get(
        Uri.parse(url),
        headers: {'User-Agent': 'Mozilla/5.0'},
      ).timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final tableData = data['table']?[0]?['data']?['table']?['all'] ?? [];
        List<Map<String, dynamic>> standings = [];

        for (var row in tableData) {
          final String tName = row['name'] ?? '';
          standings.add({
            "rank": row['idx'] ?? 0,
            "team": tName,
            "played": row['played'] ?? 0,
            "wins": row['wins'] ?? 0,
            "draws": row['draws'] ?? 0,
            "losses": row['losses'] ?? 0,
            "points": row['pts'] ?? 0,
            "logo": getLogo(tName),
          });
        }
        if (standings.isNotEmpty) return standings;
      }
    } catch (_) {}
    return [];
  }

  // 3. جلب قائمة هدافي الدوري المصري الحقيقية مباشرة
  static Future<List<Map<String, dynamic>>> getScorers() async {
    const url = 'https://www.fotmob.com/api/leagues?id=322&tab=stats&type=league&timeZone=Africa%2FCairo';

    try {
      final response = await http.get(
        Uri.parse(url),
        headers: {'User-Agent': 'Mozilla/5.0'},
      ).timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final List<dynamic> topScorersRaw = data['stats']?['players']?[0]?['topThree'] ?? 
                                           data['stats']?['players']?[0]?['data'] ?? [];
        List<Map<String, dynamic>> scorers = [];

        int rank = 1;
        for (var p in topScorersRaw) {
          final String pName = p['name'] ?? '';
          final String tName = p['teamName'] ?? '';
          scorers.add({
            "rank": rank++,
            "name": pName,
            "team": tName,
            "goals": p['value'] ?? p['count'] ?? 0,
            "photo": getLogo(tName),
          });
        }
        if (scorers.isNotEmpty) return scorers;
      }
    } catch (_) {}
    return [];
  }
}
