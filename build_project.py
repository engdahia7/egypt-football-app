import os

def write_file(path, content):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ تم تحديث: {path}")

def update_live_engine():
    print("🚀 جاري ربط التطبيق بالبيانات الحية المباشرة للدوري المصري...")

    # 1. محرك البيانات المباشر المحدث لحظياً (مباريات حقيقية + ترتيب حقيقي + هدافين)
    write_file("lib/core/football_engine.dart", r'''
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
''')

    # 2. تحديث شاشة الترتيب لتسحب البيانات الحية
    write_file("lib/screens/standings_tab.dart", r'''
import 'package:flutter/material.dart';
import '../core/football_engine.dart';

class CachedStandingsTab extends StatefulWidget {
  const CachedStandingsTab({super.key});

  @override
  State<CachedStandingsTab> createState() => _CachedStandingsTabState();
}

class _CachedStandingsTabState extends State<CachedStandingsTab> {
  bool isLoading = true;
  List<Map<String, dynamic>> table = [];

  @override
  void initState() {
    super.initState();
    loadStandings();
  }

  Future<void> loadStandings() async {
    setState(() => isLoading = true);
    final data = await FootballEngine.getStandings();
    setState(() {
      table = data;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('جدول ترتيب الدوري المصري 🏆', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
        actions: [
          IconButton(icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)), onPressed: loadStandings),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
          : table.isEmpty
              ? const Center(child: Text('جاري تحديث جدول الترتيب مع بداية الجولة...', style: TextStyle(color: Colors.white54)))
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: table.length,
                  itemBuilder: (context, index) {
                    final row = table[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 6),
                      child: ListTile(
                        dense: true,
                        leading: Text('${row['rank']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                        title: Row(
                          children: [
                            Image.network(row['logo'], width: 26, height: 26, errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 22)),
                            const SizedBox(width: 10),
                            Expanded(child: Text(row['team'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14))),
                          ],
                        ),
                        trailing: Text(
                          '${row['points']} نقطة (لعب ${row['played']})',
                          style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
''')

    # 3. تحديث شاشة الهدافين لتسحب البيانات الحية
    write_file("lib/screens/scorers_tab.dart", r'''
import 'package:flutter/material.dart';
import '../core/football_engine.dart';

class CachedScorersTab extends StatefulWidget {
  const CachedScorersTab({super.key});

  @override
  State<CachedScorersTab> createState() => _CachedScorersTabState();
}

class _CachedScorersTabState extends State<CachedScorersTab> {
  bool isLoading = true;
  List<Map<String, dynamic>> scorers = [];

  @override
  void initState() {
    super.initState();
    loadScorers();
  }

  Future<void> loadScorers() async {
    setState(() => isLoading = true);
    final data = await FootballEngine.getScorers();
    setState(() {
      scorers = data;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('قائمة الهدافين 👟⚽', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
        actions: [
          IconButton(icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)), onPressed: loadScorers),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
          : scorers.isEmpty
              ? const Center(child: Text('جاري تحديث إحصائيات الهدافين...', style: TextStyle(color: Colors.white54)))
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: scorers.length,
                  itemBuilder: (context, index) {
                    final s = scorers[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: const Color(0xFF0F172A),
                          backgroundImage: NetworkImage(s['photo']),
                        ),
                        title: Text(s['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text(s['team']),
                        trailing: Text(
                          '${s['goals']} أهداف',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
''')

    # 4. تحديث شاشة المباريات لتبدأ من تاريخ اليوم الحالي تلقائياً
    write_file("lib/screens/matches_tab.dart", r'''
import 'package:flutter/material.dart';
import '../core/football_engine.dart';
import '../widgets/match_card.dart';

class CachedMatchesTab extends StatefulWidget {
  const CachedMatchesTab({super.key});

  @override
  State<CachedMatchesTab> createState() => _CachedMatchesTabState();
}

class _CachedMatchesTabState extends State<CachedMatchesTab> {
  DateTime selectedDate = DateTime.now();
  bool isLoading = false;
  List<Map<String, dynamic>> matches = [];
  String selectedFavoriteTeam = "الأهلي";

  @override
  void initState() {
    super.initState();
    loadMatches();
  }

  String formatDate(DateTime d) =>
      "${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}";

  Future<void> loadMatches() async {
    setState(() => isLoading = true);
    final list = await FootballEngine.getMatches(formatDate(selectedDate));
    setState(() {
      matches = list;
      isLoading = false;
    });
  }

  void _chooseFavoriteTeam() {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('اختر فريقك المفضل', style: TextStyle(fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: ['الأهلي', 'الزمالك', 'بيراميدز', 'المصري', 'الاتحاد السكندري', 'الإسماعيلي'].map((name) {
            return ListTile(
              leading: const Icon(Icons.shield, color: Color(0xFF38BDF8)),
              title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              onTap: () {
                setState(() => selectedFavoriteTeam = name);
                Navigator.pop(context);
              },
            );
          }).toList(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('مباريات الكرة المصرية 🇪🇬', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
            onPressed: loadMatches,
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
            color: const Color(0xFF1E293B),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                IconButton(
                  onPressed: () {
                    setState(() => selectedDate = selectedDate.subtract(const Duration(days: 1)));
                    loadMatches();
                  },
                  icon: const Icon(Icons.arrow_back_ios, size: 18),
                ),
                Text(formatDate(selectedDate),
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8))),
                IconButton(
                  onPressed: () {
                    setState(() => selectedDate = selectedDate.add(const Duration(days: 1)));
                    loadMatches();
                  },
                  icon: const Icon(Icons.arrow_forward_ios, size: 18),
                ),
              ],
            ),
          ),
          Container(
            margin: const EdgeInsets.all(12),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.amber.withOpacity(0.5)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.stars, color: Colors.amber, size: 24),
                    const SizedBox(width: 8),
                    Text('الفريق المفضل: $selectedFavoriteTeam',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.amber)),
                  ],
                ),
                TextButton(
                  onPressed: _chooseFavoriteTeam,
                  child: const Text('تغيير', style: TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          ),
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                : matches.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.event_busy, size: 48, color: Colors.white38),
                            const SizedBox(height: 10),
                            const Text('لا توجد مباريات للدوري المصري في هذا التاريخ 📅', style: TextStyle(color: Colors.white54)),
                            const SizedBox(height: 6),
                            const Text('استخدم الأسهم العلوية لمتابعة الجولات القادمة أو السابقة', style: TextStyle(color: Colors.white38, fontSize: 11)),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        itemCount: matches.length,
                        itemBuilder: (context, index) => MatchCard(match: matches[index]),
                      ),
          ),
        ],
      ),
    );
  }
}
''')

    print("\n🎉 تم تحديث المشروع بالكامل لجلب البيانات الحية الحقيقية بنجاح!");

if __name__ == "__main__":
    update_live_engine()