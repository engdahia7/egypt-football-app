import os

# ضع مفتاح API-Football الخاص بك هنا
API_KEY = "YOUR_API_KEY_HERE"

def write_file(path, content):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ تم تحديث: {path}")

def update_all():
    print("🚀 جاري تثبيت المحرك المستقر وإصلاح الاتصال والأيقونة...")

    # 1. إعدادات البناء وتوليد الأيقونة المخصصة وتصريح الشبكة
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

      - name: Add Permissions & Config
        run: |
          sed -i 's/<application/<uses-permission android:name="android.permission.INTERNET"\/><uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"\/><application android:usesCleartextTraffic="true"/g' android/app/src/main/AndroidManifest.xml
          sed -i 's/android:label="[^"]*"/android:label="الكرة المصرية"/g' android/app/src/main/AndroidManifest.xml

      - name: Setup App Icon
        run: |
          curl -sL "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/26bd.png" -o ball.png
          for res in mipmap-mdpi mipmap-hdpi mipmap-xhdpi mipmap-xxhdpi mipmap-xxxhdpi; do
            mkdir -p android/app/src/main/res/$res
            cp ball.png android/app/src/main/res/$res/ic_launcher.png
          done

      - name: Get Dependencies
        run: flutter pub get

      - name: Build Optimized Split APK
        run: flutter build apk --release --split-per-abi

      - name: Upload Compact APK
        uses: actions/upload-artifact@v4
        with:
          name: Egyptian-Football-Final-APK
          path: build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
''')

    # 2. مدير الكاش المباشر والآمن لـ API-Football
    write_file("lib/core/smart_api_cache.dart", f'''
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class SmartApiCache {{
  static const String apiKey = '{API_KEY}';

  static Future<Map<String, dynamic>> get({{
    required String cacheKey,
    required String url,
    required Duration ttl,
    bool forceRefresh = false,
  }}) async {{
    final prefs = await SharedPreferences.getInstance();
    final String? cachedJson = prefs.getString('cache_$cacheKey');
    final int? cachedTime = prefs.getInt('time_$cacheKey');
    final int now = DateTime.now().millisecondsSinceEpoch;

    if (!forceRefresh && cachedJson != null && cachedTime != null) {{
      final int ageInMinutes = ((now - cachedTime) / 60000).round();
      if (ageInMinutes < ttl.inMinutes) {{
        return json.decode(cachedJson);
      }}
    }}

    try {{
      final response = await http.get(
        Uri.parse(url),
        headers: {{
          'x-apisports-key': apiKey,
          'Accept': 'application/json',
        }},
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {{
        final Map<String, dynamic> data = json.decode(response.body);
        if (data['errors'] == null || (data['errors'] as dynamic).isEmpty) {{
          await prefs.setString('cache_$cacheKey', response.body);
          await prefs.setInt('time_$cacheKey', now);
        }}
        return data;
      }} else {{
        throw Exception('Server responded with code: ${{response.statusCode}}');
      }}
    }} catch (e) {{
      if (cachedJson != null) {{
        return json.decode(cachedJson);
      }}
      rethrow;
    }}
  }}
}}
''')

    # 3. شاشة المباريات مع عرض رسالة الخطأ بالتفصيل إن وجدت
    write_file("lib/screens/matches_tab.dart", r'''
import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../core/smart_api_cache.dart';
import '../models/favorite_team.dart';
import '../widgets/favorite_team_banner.dart';
import '../widgets/match_card.dart';

class CachedMatchesTab extends StatefulWidget {
  const CachedMatchesTab({super.key});

  @override
  State<CachedMatchesTab> createState() => _CachedMatchesTabState();
}

class _CachedMatchesTabState extends State<CachedMatchesTab> {
  DateTime selectedDate = DateTime.now();
  bool isLoading = false;
  List<dynamic> filteredMatches = [];
  FavoriteTeam? favoriteTeam;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _initData();
  }

  Future<void> _initData() async {
    favoriteTeam = await FavoriteTeamManager.getFavorite();
    await loadMatches();
  }

  String formatDate(DateTime date) =>
      "${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}";

  Future<void> loadMatches({bool forceRefresh = false}) async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    final String dateStr = formatDate(selectedDate);
    final String url =
        'https://v3.football.api-sports.io/fixtures?date=$dateStr&timezone=Africa/Cairo';

    try {
      final data = await SmartApiCache.get(
        cacheKey: 'matches_$dateStr',
        url: url,
        ttl: dateStr == formatDate(DateTime.now())
            ? const Duration(minutes: 15)
            : const Duration(hours: 6),
        forceRefresh: forceRefresh,
      );

      final List<dynamic> allMatches = data['response'] ?? [];
      final List<dynamic> egyptMatches = allMatches.where((match) {
        final int leagueId = match['league']['id'];
        final String country = match['league']['country'] ?? '';
        final int homeId = match['teams']['home']['id'];
        final int awayId = match['teams']['away']['id'];

        return country == 'Egypt' ||
            AppConstants.egyptianLeagueIds.contains(leagueId) ||
            AppConstants.egyptianTeamIds.contains(homeId) ||
            AppConstants.egyptianTeamIds.contains(awayId);
      }).toList();

      setState(() {
        filteredMatches = egyptMatches;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMessage = 'خطأ في الاتصال: $e';
        isLoading = false;
      });
    }
  }

  void _openTeamSelector() {
    showDialog(
      context: context,
      builder: (_) => SelectFavoriteTeamDialog(
        onTeamSelected: (team) async {
          await FavoriteTeamManager.saveFavorite(team);
          setState(() => favoriteTeam = team);
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('مباريات الكرة المصرية 🇪🇬',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
            tooltip: 'تحديث فوري',
            onPressed: () => loadMatches(forceRefresh: true),
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
                    setState(() => selectedDate =
                        selectedDate.subtract(const Duration(days: 1)));
                    loadMatches();
                  },
                  icon: const Icon(Icons.arrow_back_ios, size: 18),
                ),
                Text(formatDate(selectedDate),
                    style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF38BDF8))),
                IconButton(
                  onPressed: () {
                    setState(() => selectedDate =
                        selectedDate.add(const Duration(days: 1)));
                    loadMatches();
                  },
                  icon: const Icon(Icons.arrow_forward_ios, size: 18),
                ),
              ],
            ),
          ),
          FavoriteTeamBanner(
            favoriteTeam: favoriteTeam,
            allMatches: filteredMatches,
            onSelectTeamClicked: _openTeamSelector,
          ),
          Expanded(
            child: isLoading
                ? const Center(
                    child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                : errorMessage != null
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(errorMessage!,
                                  textAlign: TextAlign.center,
                                  style: const TextStyle(
                                      color: Colors.redAccent, fontSize: 13)),
                              const SizedBox(height: 12),
                              ElevatedButton(
                                onPressed: () => loadMatches(forceRefresh: true),
                                child: const Text('إعادة المحاولة'),
                              ),
                            ],
                          ),
                        ),
                      )
                    : filteredMatches.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(Icons.event_busy,
                                    size: 48, color: Colors.white38),
                                const SizedBox(height: 10),
                                const Text(
                                  'لا توجد مباريات مسجلة للفرق المصرية في هذا اليوم 📅',
                                  style: TextStyle(
                                      color: Colors.white54, fontSize: 13),
                                ),
                                const SizedBox(height: 6),
                                const Text(
                                  'تنقل بالأسهم العلوية للاطلاع على مواعيد الجولات القادمة',
                                  style: TextStyle(
                                      color: Colors.white38, fontSize: 11),
                                ),
                              ],
                            ),
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.symmetric(horizontal: 12),
                            itemCount: filteredMatches.length,
                            itemBuilder: (context, index) =>
                                MatchCard(match: filteredMatches[index]),
                          ),
          ),
        ],
      ),
    );
  }
}
''')

    # 4. كارت المباراة
    write_file("lib/widgets/match_card.dart", r'''
import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../screens/match_details_screen.dart';

class MatchCard extends StatelessWidget {
  final dynamic match;
  const MatchCard({super.key, required this.match});

  @override
  Widget build(BuildContext context) {
    final home = match['teams']['home'];
    final away = match['teams']['away'];
    final goals = match['goals'];
    final status = match['fixture']['status'];
    final String shortStatus = status['short'] ?? 'NS';
    final int? elapsed = status['elapsed'];
    final String matchTime = match['fixture']['date'].substring(11, 16);

    final bool isLive = ['1H', '2H', 'HT', 'ET', 'P'].contains(shortStatus);
    final bool isFinished = ['FT', 'AET', 'PEN'].contains(shortStatus);

    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => Directionality(
              textDirection: TextDirection.rtl,
              child: MatchDetailsScreen(fixtureId: match['fixture']['id']),
            ),
          ),
        );
      },
      child: Card(
        margin: const EdgeInsets.only(bottom: 10),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  children: [
                    Image.network(home['logo'], width: 38, height: 38,
                        errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 36)),
                    const SizedBox(height: 6),
                    Text(AppConstants.translate(home['name']),
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    Text(
                      (isLive || isFinished)
                          ? '${goals['home'] ?? 0}  -  ${goals['away'] ?? 0}'
                          : matchTime,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: (isLive || isFinished) ? Colors.white : const Color(0xFF38BDF8),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      isLive ? 'مباشر $elapsed\'' : (isFinished ? 'انتهت' : 'لم تبدأ'),
                      style: TextStyle(
                        fontSize: 11,
                        color: isLive ? Colors.redAccent : (isFinished ? Colors.greenAccent : Colors.white54),
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Column(
                  children: [
                    Image.network(away['logo'], width: 38, height: 38,
                        errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 36)),
                    const SizedBox(height: 6),
                    Text(AppConstants.translate(away['name']),
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
''')

    print("\n🎉 تم تحديث السكريبت بنجاح تام!");

if __name__ == "__main__":
    update_all()