import os

def write_file(path, content):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ تم تحديث: {path}")

def update_all():
    print("🚀 جاري إصلاح الأيقونة ورابط المباريات...")

    # 1. تحديث سيرفر البناء مع توليد أيقونة مخصصة للتطبيق تلقائياً
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

      - name: Add Internet Permission & App Name
        run: |
          sed -i 's/<application/<uses-permission android:name="android.permission.INTERNET"\/><application/g' android/app/src/main/AndroidManifest.xml
          sed -i 's/android:label="[^"]*"/android:label="الكرة المصرية"/g' android/app/src/main/AndroidManifest.xml

      # تحميل وتثبيت أيقونة كرة قدم عربية مخصصة بدلاً من أيقونة فلاتر
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

    # 2. تحديث شاشة المباريات لمعالجة البيانات وعرضها بدقة
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
  List<dynamic> matches = [];
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

  String format365Date(DateTime d) =>
      "${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year}";

  String formatDisplayDate(DateTime d) =>
      "${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}";

  Future<void> loadMatches({bool forceRefresh = false}) async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    final String dateParam = format365Date(selectedDate);
    // رابط محسّن يجلب مباريات اليوم مع تحديد البلد (مصر) والبطولات
    final String url =
        'https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=27&timezoneName=Africa/Cairo&userCountryId=131&startDate=$dateParam&endDate=$dateParam&competitions=${AppConstants.egyptCompetitions}';

    try {
      final data = await SmartApiCache.get(
        cacheKey: '365_matches_${formatDisplayDate(selectedDate)}',
        url: url,
        ttl: const Duration(minutes: 2),
        forceRefresh: forceRefresh,
      );

      final List<dynamic> games = data['games'] ?? [];

      setState(() {
        matches = games;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMessage = 'تعذر تحميل المباريات، تأكد من الاتصال بالإنترنت.';
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
          // شريط اختيار التاريخ
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
                Text(formatDisplayDate(selectedDate),
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
            allMatches: matches,
            onSelectTeamClicked: _openTeamSelector,
          ),
          Expanded(
            child: isLoading
                ? const Center(
                    child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                : errorMessage != null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(errorMessage!,
                                style: const TextStyle(color: Colors.redAccent)),
                            const SizedBox(height: 10),
                            ElevatedButton(
                              onPressed: () => loadMatches(forceRefresh: true),
                              child: const Text('إعادة المحاولة'),
                            ),
                          ],
                        ),
                      )
                    : matches.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(Icons.event_busy,
                                    size: 48, color: Colors.white38),
                                const SizedBox(height: 10),
                                const Text(
                                  'لا توجد مباريات مسجلة لهذا التاريخ 📅',
                                  style: TextStyle(
                                      color: Colors.white54, fontSize: 14),
                                ),
                                const SizedBox(height: 6),
                                const Text(
                                  'جرب التبديل لأيام أخرى باستخدام الأسهم في الأعلى',
                                  style: TextStyle(
                                      color: Colors.white38, fontSize: 12),
                                ),
                              ],
                            ),
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.symmetric(horizontal: 12),
                            itemCount: matches.length,
                            itemBuilder: (context, index) =>
                                MatchCard(match: matches[index]),
                          ),
          ),
        ],
      ),
    );
  }
}
''')

    print("\n🎉 تم تحديث الإعدادات والأيقونة بنجاح!");

if __name__ == "__main__":
    update_all()