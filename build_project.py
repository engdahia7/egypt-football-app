import os

def write_file(path, content):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ تم تحديث: {path}")

def update_365_mobile():
    print("🚀 جاري ضبط التطبيق على سيرفر موبايل 365Scores الرسمي بدون مفتاح...")

    # 1. إعدادات الحزم
    write_file("pubspec.yaml", r'''
name: egyptian_football_app
description: تطبيق الكرة المصرية
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.2.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0
  shared_preferences: ^2.2.3
  share_plus: ^10.1.2
  path_provider: ^2.1.3

dev_dependencies:
  flutter_test:
    sdk: flutter

flutter:
  uses-material-design: true
''')

    # 2. خط أنابيب البناء السحابي والأيقونة
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
          name: Egyptian-Football-365-APK
          path: build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
''')

    # 3. الثوابت والأكواد الخاصة بـ 365Scores
    write_file("lib/core/app_constants.dart", r'''
class AppConstants {
  // 552: الدوري المصري | 553: كأس مصر | 1129: السوبر المصري | 572: دوري أبطال أفريقيا | 573: الكونفدرالية
  static const String egyptCompetitions = '552,553,1129,572,573';

  static String teamLogo(int teamId) =>
      'https://imagecache.365scores.com/image/upload/f_png,w_80,h_80,c_limit,q_auto:eco,d_Competitors:default1.png/v1/Competitors/$teamId';

  static String playerPhoto(int athleteId) =>
      'https://imagecache.365scores.com/image/upload/f_png,w_80,h_80,c_limit,q_auto:eco,d_Athletes:default.png/v1/Athletes/$athleteId';
}
''')

    # 4. مدير الكاش والاتصال بسيرفر الموبايل (بدون مفتاح)
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
''')

    # 5. موديل الفريق المفضل
    write_file("lib/models/favorite_team.dart", r'''
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
''')

    # 6. شريط الفريق المفضل
    write_file("lib/widgets/favorite_team_banner.dart", r'''
import 'package:flutter/material.dart';
import '../models/favorite_team.dart';

class FavoriteTeamBanner extends StatelessWidget {
  final FavoriteTeam? favoriteTeam;
  final List<dynamic> allMatches;
  final VoidCallback onSelectTeamClicked;

  const FavoriteTeamBanner({
    super.key,
    required this.favoriteTeam,
    required this.allMatches,
    required this.onSelectTeamClicked,
  });

  @override
  Widget build(BuildContext context) {
    if (favoriteTeam == null) {
      return Container(
        margin: const EdgeInsets.all(12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFF38BDF8).withOpacity(0.3)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Row(
              children: [
                Icon(Icons.star, color: Colors.amber, size: 22),
                SizedBox(width: 10),
                Text('اختر فريقك المفضل لمتابعة مبارياته',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
              ],
            ),
            TextButton(
              onPressed: onSelectTeamClicked,
              child: const Text('اختيار',
                  style: TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      );
    }

    dynamic teamMatch;
    for (var m in allMatches) {
      final String hName = m['homeCompetitor']?['name'] ?? '';
      final String aName = m['awayCompetitor']?['name'] ?? '';
      if (hName.contains(favoriteTeam!.name) || aName.contains(favoriteTeam!.name)) {
        teamMatch = m;
        break;
      }
    }

    return Container(
      margin: const EdgeInsets.all(12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF1E293B), Color(0xFF0F172A)]),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.amber.withOpacity(0.4), width: 1.2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.stars, color: Colors.amber, size: 22),
                  const SizedBox(width: 8),
                  Text('مباريات ${favoriteTeam!.name}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.amber)),
                ],
              ),
              GestureDetector(
                onTap: onSelectTeamClicked,
                child: const Text('تغيير', style: TextStyle(fontSize: 12, color: Color(0xFF38BDF8))),
              ),
            ],
          ),
          const Divider(height: 16, color: Colors.white12),
          teamMatch == null
              ? const Text('لا توجد مباراة مسجلة لهذا الفريق في هذا التاريخ 📅',
                  style: TextStyle(fontSize: 12, color: Colors.white60))
              : Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(teamMatch['homeCompetitor']['name'] ?? '',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        teamMatch['statusGroup'] == 2
                            ? (teamMatch['startTime'] ?? '').toString().substring(11, 16)
                            : '${teamMatch['homeCompetitor']['score'] ?? 0} - ${teamMatch['awayCompetitor']['score'] ?? 0}',
                        style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
                      ),
                    ),
                    Expanded(
                      child: Text(teamMatch['awayCompetitor']['name'] ?? '',
                          textAlign: TextAlign.left,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    ),
                  ],
                ),
        ],
      ),
    );
  }
}

class SelectFavoriteTeamDialog extends StatelessWidget {
  final Function(FavoriteTeam) onTeamSelected;
  const SelectFavoriteTeamDialog({super.key, required this.onTeamSelected});

  final List<String> egyptianTeams = const [
    'الأهلي', 'الزمالك', 'بيراميدز', 'المصري', 'الاتحاد السكندري',
    'الإسماعيلي', 'سيراميكا كليوباترا', 'مودرن سبورت', 'سموحة', 'إنبي',
    'غزل المحلة', 'زد', 'مصر'
  ];

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: const Color(0xFF1E293B),
      title: const Text('اختر فريقك المفضل', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
      content: SizedBox(
        width: double.maxFinite,
        child: ListView.builder(
          shrinkWrap: true,
          itemCount: egyptianTeams.length,
          itemBuilder: (context, index) {
            final name = egyptianTeams[index];
            return ListTile(
              leading: const Icon(Icons.shield, color: Color(0xFF38BDF8)),
              title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              onTap: () {
                onTeamSelected(FavoriteTeam(name: name, logo: ''));
                Navigator.pop(context);
              },
            );
          },
        ),
      ),
    );
  }
}
''')

    # 7. ملعب التشكيل
    write_file("lib/widgets/soccer_pitch_widget.dart", r'''
import 'package:flutter/material.dart';

class SoccerPitchWidget extends StatelessWidget {
  final Map<String, dynamic> homeComp;
  final Map<String, dynamic> awayComp;

  const SoccerPitchWidget({super.key, required this.homeComp, required this.awayComp});

  @override
  Widget build(BuildContext context) {
    final List<dynamic> homeMembers = homeComp['lineups']?['members'] ?? [];
    final List<dynamic> awayMembers = awayComp['lineups']?['members'] ?? [];

    final List<dynamic> homeStarting = homeMembers.where((m) => m['status'] == 1).toList();
    final List<dynamic> awayStarting = awayMembers.where((m) => m['status'] == 1).toList();

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      height: 620,
      width: double.infinity,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            Positioned.fill(child: CustomPaint(painter: PitchPainter())),
            ..._buildTeamFormation(
              players: homeStarting,
              formationStr: homeComp['lineups']?['formation'] ?? '4-3-3',
              isHome: true,
              shirtColor: const Color(0xFF0284C7),
            ),
            ..._buildTeamFormation(
              players: awayStarting,
              formationStr: awayComp['lineups']?['formation'] ?? '4-3-3',
              isHome: false,
              shirtColor: const Color(0xFFE11D48),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildTeamFormation({
    required List<dynamic> players,
    required String formationStr,
    required bool isHome,
    required Color shirtColor,
  }) {
    if (players.isEmpty) return [];

    final List<int> rowsCounts = [1];
    for (var part in formationStr.split('-')) {
      final int? count = int.tryParse(part.trim());
      if (count != null && count > 0) rowsCounts.add(count);
    }
    if (rowsCounts.length == 1) rowsCounts.addAll([4, 4, 2]);

    List<Widget> widgets = [];
    int playerIdx = 0;
    final int totalRows = rowsCounts.length;

    for (int r = 0; r < totalRows; r++) {
      final int colsInThisRow = rowsCounts[r];
      for (int c = 0; c < colsInThisRow; c++) {
        if (playerIdx >= players.length) break;
        final p = players[playerIdx++];

        double xAlign = 0.0;
        if (colsInThisRow > 1) {
          double normX = c / (colsInThisRow - 1);
          if (!isHome) normX = 1.0 - normX;
          xAlign = -0.78 + (normX * 1.56);
        }

        double normY = totalRows > 1 ? r / (totalRows - 1) : 0.0;
        double yAlign = isHome ? -0.90 + (normY * 0.76) : 0.90 - (normY * 0.76);

        final String name = p['athlete']?['name'] ?? p['name'] ?? '';
        final String jersey = '${p['jerseyNumber'] ?? p['formation']?['number'] ?? ''}';

        widgets.add(
          Align(
            alignment: Alignment(xAlign, yAlign),
            child: SizedBox(
              width: 68,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 30,
                    height: 30,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: r == 0 ? Colors.amber.shade700 : shirtColor,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 1.8),
                    ),
                    child: Text(jersey, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
                  ),
                  const SizedBox(height: 2),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                    decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(4)),
                    child: Text(
                      name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 9.5, color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }
    }
    return widgets;
  }
}

class PitchPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    const int stripes = 12;
    final double stripeHeight = size.height / stripes;
    for (int i = 0; i < stripes; i++) {
      canvas.drawRect(
        Rect.fromLTWH(0, i * stripeHeight, size.width, stripeHeight),
        Paint()..color = i.isEven ? const Color(0xFF15803D) : const Color(0xFF166534),
      );
    }
    final Paint linePaint = Paint()
      ..color = Colors.white70
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6;

    const double pad = 12.0;
    final double w = size.width;
    final double h = size.height;

    canvas.drawRect(Rect.fromLTWH(pad, pad, w - pad * 2, h - pad * 2), linePaint);
    canvas.drawLine(Offset(pad, h / 2), Offset(w - pad, h / 2), linePaint);
    canvas.drawCircle(Offset(w / 2, h / 2), 42, linePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
''')

    # 8. أداة المشاركة
    write_file("lib/widgets/share_card_helper.dart", r'''
import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class ShareableMatchWidget extends StatefulWidget {
  final Widget child;
  final String shareText;
  const ShareableMatchWidget({super.key, required this.child, required this.shareText});

  @override
  State<ShareableMatchWidget> createState() => ShareableMatchWidgetState();
}

class ShareableMatchWidgetState extends State<ShareableMatchWidget> {
  final GlobalKey _boundaryKey = GlobalKey();

  Future<void> captureAndShare() async {
    try {
      final RenderRepaintBoundary? boundary = _boundaryKey.currentContext?.findRenderObject() as RenderRepaintBoundary?;
      if (boundary == null) return;
      final ui.Image image = await boundary.toImage(pixelRatio: 3.0);
      final ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      if (byteData != null) {
        final Uint8List pngBytes = byteData.buffer.asUint8List();
        final Directory tempDir = await getTemporaryDirectory();
        final File imgFile = File('${tempDir.path}/match_${DateTime.now().millisecondsSinceEpoch}.png');
        await imgFile.writeAsBytes(pngBytes);
        await Share.shareXFiles([XFile(imgFile.path)], text: widget.shareText);
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      key: _boundaryKey,
      child: Container(
        color: const Color(0xFF0F172A),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            widget.child,
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 14),
              color: const Color(0xFF1E293B),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('تطبيق الكرة المصرية 🇪🇬⚽', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
                  Text('مباشر لحظة بلحظة 📲', style: TextStyle(fontSize: 10, color: Color(0xFF38BDF8))),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
''')

    # 9. شاشة تفاصيل المباراة
    write_file("lib/screens/match_details_screen.dart", r'''
import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../core/smart_api_cache.dart';
import '../widgets/soccer_pitch_widget.dart';
import '../widgets/share_card_helper.dart';

class MatchDetailsScreen extends StatefulWidget {
  final int gameId;
  const MatchDetailsScreen({super.key, required this.gameId});

  @override
  State<MatchDetailsScreen> createState() => _MatchDetailsScreenState();
}

class _MatchDetailsScreenState extends State<MatchDetailsScreen> {
  bool isLoading = true;
  Map<String, dynamic>? gameData;
  final GlobalKey<ShareableMatchWidgetState> _scoreShareKey = GlobalKey();
  final GlobalKey<ShareableMatchWidgetState> _pitchShareKey = GlobalKey();

  @override
  void initState() {
    super.initState();
    fetchDetails();
  }

  Future<void> fetchDetails({bool forceRefresh = false}) async {
    setState(() => isLoading = true);
    try {
      final data = await SmartApiCache.get(
        cacheKey: 'game_${widget.gameId}',
        url: 'https://appws.365scores.com/web/game/?langId=27&timezoneName=Africa/Cairo&userCountryId=131&gameId=${widget.gameId}',
        ttl: const Duration(minutes: 1),
        forceRefresh: forceRefresh,
      );
      setState(() {
        gameData = data['game'];
        isLoading = false;
      });
    } catch (_) {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: const Color(0xFF1E293B),
          title: Text(gameData?['competitionDisplayName'] ?? 'تفاصيل المباراة', style: const TextStyle(fontSize: 16)),
          actions: [
            IconButton(
              icon: const Icon(Icons.share, color: Colors.greenAccent),
              onPressed: () => _scoreShareKey.currentState?.captureAndShare(),
            ),
            IconButton(
              icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
              onPressed: () => fetchDetails(forceRefresh: true),
            ),
          ],
          bottom: const TabBar(
            indicatorColor: Color(0xFF38BDF8),
            tabs: [
              Tab(text: 'الأحداث ⏱️'),
              Tab(text: 'التشكيل 👕'),
              Tab(text: 'الإحصائيات 📊'),
            ],
          ),
        ),
        body: isLoading || gameData == null
            ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
            : Column(
                children: [
                  ShareableMatchWidget(
                    key: _scoreShareKey,
                    shareText: 'نتيجة المباراة عبر تطبيق الكرة المصرية 🇪🇬',
                    child: _buildHeader(),
                  ),
                  Expanded(
                    child: TabBarView(
                      children: [
                        _buildEventsTab(),
                        _buildLineupsTab(),
                        _buildStatsTab(),
                      ],
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildHeader() {
    final home = gameData!['homeCompetitor'] ?? {};
    final away = gameData!['awayCompetitor'] ?? {};
    final int hScore = (home['score'] ?? -1).toInt();
    final int aScore = (away['score'] ?? -1).toInt();
    final String tvNetwork = (gameData!['tvNetworks'] as List?)?.isNotEmpty == true
        ? gameData!['tvNetworks'][0]['name'] ?? ''
        : '';

    return Container(
      padding: const EdgeInsets.all(16),
      color: const Color(0xFF1E293B),
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  children: [
                    Image.network(AppConstants.teamLogo(home['id'] ?? 0), width: 48, height: 48,
                        errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 44)),
                    const SizedBox(height: 6),
                    Text(home['name'] ?? '', textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
              Column(
                children: [
                  Text(hScore >= 0 ? '$hScore : $aScore' : 'VS',
                      style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(gameData!['statusText'] ?? '', style: const TextStyle(fontSize: 12, color: Color(0xFF38BDF8))),
                ],
              ),
              Expanded(
                child: Column(
                  children: [
                    Image.network(AppConstants.teamLogo(away['id'] ?? 0), width: 48, height: 48,
                        errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 44)),
                    const SizedBox(height: 6),
                    Text(away['name'] ?? '', textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            ],
          ),
          if (tvNetwork.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text('📺 القناة الناقلة: $tvNetwork', style: const TextStyle(fontSize: 11, color: Colors.amber)),
          ]
        ],
      ),
    );
  }

  Widget _buildEventsTab() {
    final List<dynamic> events = gameData!['events'] ?? [];
    if (events.isEmpty) return const Center(child: Text('لا توجد أحداث مسجلة في هذه المباراة بعد'));

    final Map<int, String> membersMap = {};
    for (var m in (gameData!['members'] ?? [])) {
      membersMap[m['id']] = m['name'] ?? '';
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: events.length,
      itemBuilder: (context, index) {
        final e = events[index];
        final String playerName = membersMap[e['playerId']] ?? '';
        final String eventType = e['eventType']?['name'] ?? '';
        final String timeStr = '${e['gameTimeDisplay'] ?? e['gameTime'] ?? ''}\'';

        return Card(
          child: ListTile(
            leading: Text(timeStr, style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold)),
            title: Text('$eventType - $playerName', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
          ),
        );
      },
    );
  }

  Widget _buildLineupsTab() {
    final home = gameData!['homeCompetitor'] ?? {};
    final away = gameData!['awayCompetitor'] ?? {};
    final bool hasLineup = home['lineups']?['members'] != null;

    if (!hasLineup) {
      return const Center(child: Text('التشكيل الرسمي لم يصدر بعد'));
    }

    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        ElevatedButton.icon(
          onPressed: () => _pitchShareKey.currentState?.captureAndShare(),
          icon: const Icon(Icons.share),
          label: const Text('مشاركة رسمة التشكيل على واتساب 📲'),
        ),
        ShareableMatchWidget(
          key: _pitchShareKey,
          shareText: 'التشكيل الرسمي للمباراة 🇪🇬📋',
          child: SoccerPitchWidget(homeComp: home, awayComp: away),
        ),
      ],
    );
  }

  Widget _buildStatsTab() {
    final List<dynamic> stats = gameData!['statistics'] ?? [];
    if (stats.isEmpty) return const Center(child: Text('لا تتوفر إحصائيات لهذه المباراة حالياً'));

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: stats.length,
      itemBuilder: (context, index) {
        final s = stats[index];
        return Padding(
          padding: const EdgeInsets.only(bottom: 14),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('${s['homeValue'] ?? '-'}', style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF38BDF8))),
              Text('${s['name'] ?? ''}', style: const TextStyle(color: Colors.white70)),
              Text('${s['awayValue'] ?? '-'}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.amber)),
            ],
          ),
        );
      },
    );
  }
}
''')

    # 10. كارت المباراة
    write_file("lib/widgets/match_card.dart", r'''
import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../screens/match_details_screen.dart';

class MatchCard extends StatelessWidget {
  final dynamic match;
  const MatchCard({super.key, required this.match});

  @override
  Widget build(BuildContext context) {
    final home = match['homeCompetitor'] ?? {};
    final away = match['awayCompetitor'] ?? {};
    final int homeId = home['id'] ?? 0;
    final int awayId = away['id'] ?? 0;
    final int homeScore = (home['score'] ?? -1).toInt();
    final int awayScore = (away['score'] ?? -1).toInt();

    final int statusGroup = match['statusGroup'] ?? 2;
    final String statusText = match['statusText'] ?? '';
    final String compName = match['competitionDisplayName'] ?? '';
    final String startTimeStr = match['startTime'] ?? '';
    final String timeOnly = startTimeStr.length >= 16 ? startTimeStr.substring(11, 16) : '';

    final bool isLive = statusGroup == 3;
    final bool isFinished = statusGroup == 4;
    final bool hasScore = homeScore >= 0 && awayScore >= 0;

    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => Directionality(
              textDirection: TextDirection.rtl,
              child: MatchDetailsScreen(gameId: match['id']),
            ),
          ),
        );
      },
      child: Card(
        margin: const EdgeInsets.only(bottom: 10),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
          child: Column(
            children: [
              Text(
                compName,
                style: const TextStyle(fontSize: 11, color: Colors.amber, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: Column(
                      children: [
                        Image.network(
                          AppConstants.teamLogo(homeId),
                          width: 38,
                          height: 38,
                          errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 36),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          home['name'] ?? '',
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                        ),
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
                          hasScore ? '$homeScore  -  $awayScore' : timeOnly,
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: hasScore ? Colors.white : const Color(0xFF38BDF8),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          isLive ? '🔴 $statusText (${match['gameTimeDisplay'] ?? ''})' : statusText,
                          style: TextStyle(
                            fontSize: 11,
                            color: isLive
                                ? Colors.redAccent
                                : (isFinished ? Colors.greenAccent : Colors.white54),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: Column(
                      children: [
                        Image.network(
                          AppConstants.teamLogo(awayId),
                          width: 38,
                          height: 38,
                          errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 36),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          away['name'] ?? '',
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
''')

    # 11. شاشة المباريات
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
    final String url =
        'https://appws.365scores.com/web/games/allscores/?langId=27&timezoneName=Africa/Cairo&userCountryId=131&startDate=$dateParam&endDate=$dateParam&competitions=${AppConstants.egyptCompetitions}';

    try {
      final data = await SmartApiCache.get(
        cacheKey: 'matches_${formatDisplayDate(selectedDate)}',
        url: url,
        ttl: const Duration(minutes: 2),
        forceRefresh: forceRefresh,
      );

      setState(() {
        matches = data['games'] ?? [];
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMessage = 'خطأ في الاتصال بالسيرفر: $e';
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
                    : matches.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(Icons.event_busy,
                                    size: 48, color: Colors.white38),
                                const SizedBox(height: 10),
                                const Text(
                                  'لا توجد مباريات مسجلة في هذا اليوم 📅',
                                  style: TextStyle(
                                      color: Colors.white54, fontSize: 14),
                                ),
                                const SizedBox(height: 6),
                                const Text(
                                  'استخدم الأسهم العلوية للتنقل بين الأيام',
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

    # 12. جدول الترتيب
    write_file("lib/screens/standings_tab.dart", r'''
import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../core/smart_api_cache.dart';

class CachedStandingsTab extends StatefulWidget {
  const CachedStandingsTab({super.key});

  @override
  State<CachedStandingsTab> createState() => _CachedStandingsTabState();
}

class _CachedStandingsTabState extends State<CachedStandingsTab> {
  int selectedCompId = 552;
  bool isLoading = false;
  List<dynamic> rows = [];

  @override
  void initState() {
    super.initState();
    loadStandings();
  }

  Future<void> loadStandings({bool forceRefresh = false}) async {
    setState(() => isLoading = true);
    try {
      final data = await SmartApiCache.get(
        cacheKey: 'standings_$selectedCompId',
        url: 'https://appws.365scores.com/web/standings/?langId=27&timezoneName=Africa/Cairo&userCountryId=131&competitions=$selectedCompId',
        ttl: const Duration(hours: 1),
        forceRefresh: forceRefresh,
      );
      final List<dynamic> standingsList = data['standings'] ?? [];
      setState(() {
        rows = standingsList.isNotEmpty ? (standingsList.first['rows'] ?? []) : [];
        isLoading = false;
      });
    } catch (_) {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('جدول الترتيب 🏆', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
            onPressed: () => loadStandings(forceRefresh: true),
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            color: const Color(0xFF1E293B),
            padding: const EdgeInsets.all(10),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildChip(552, 'الدوري المصري'),
                _buildChip(572, 'أبطال أفريقيا'),
                _buildChip(573, 'الكونفدرالية'),
              ],
            ),
          ),
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                : rows.isEmpty
                    ? const Center(child: Text('لا توجد جداول متاحة حالياً'))
                    : ListView.builder(
                        padding: const EdgeInsets.all(12),
                        itemCount: rows.length,
                        itemBuilder: (context, index) {
                          final r = rows[index];
                          final comp = r['competitor'] ?? {};
                          return Card(
                            margin: const EdgeInsets.only(bottom: 6),
                            child: ListTile(
                              dense: true,
                              leading: Text('${r['position'] ?? (index + 1)}',
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                              title: Row(
                                children: [
                                  Image.network(
                                    AppConstants.teamLogo(comp['id'] ?? 0),
                                    width: 24,
                                    height: 24,
                                    errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 20),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(comp['name'] ?? '',
                                        style: const TextStyle(fontWeight: FontWeight.bold)),
                                  ),
                                ],
                              ),
                              trailing: Text(
                                '${(r['points'] ?? 0).toInt()} نقطة (لعب ${(r['gamePlayed'] ?? 0).toInt()})',
                                style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold),
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildChip(int id, String label) {
    final bool active = selectedCompId == id;
    return ChoiceChip(
      label: Text(label),
      selected: active,
      selectedColor: const Color(0xFF38BDF8),
      labelStyle: TextStyle(color: active ? Colors.black : Colors.white, fontSize: 12),
      onSelected: (_) {
        setState(() => selectedCompId = id);
        loadStandings();
      },
    );
  }
}
''')

    # 13. قائمة الهدافين
    write_file("lib/screens/scorers_tab.dart", r'''
import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../core/smart_api_cache.dart';

class CachedScorersTab extends StatefulWidget {
  const CachedScorersTab({super.key});

  @override
  State<CachedScorersTab> createState() => _CachedScorersTabState();
}

class _CachedScorersTabState extends State<CachedScorersTab> {
  int selectedCompId = 552;
  bool isLoading = false;
  List<dynamic> scorers = [];

  @override
  void initState() {
    super.initState();
    loadScorers();
  }

  Future<void> loadScorers({bool forceRefresh = false}) async {
    setState(() => isLoading = true);
    try {
      final data = await SmartApiCache.get(
        cacheKey: 'scorers_$selectedCompId',
        url: 'https://appws.365scores.com/web/stats/?langId=27&timezoneName=Africa/Cairo&userCountryId=131&competitions=$selectedCompId',
        ttl: const Duration(hours: 2),
        forceRefresh: forceRefresh,
      );

      final List<dynamic> athletesStats = data['stats']?['athletesStats'] ?? [];
      setState(() {
        scorers = athletesStats.isNotEmpty ? (athletesStats.first['rows'] ?? []) : [];
        isLoading = false;
      });
    } catch (_) {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('قائمة الهدافين 👟⚽', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
            onPressed: () => loadScorers(forceRefresh: true),
          ),
        ],
      ),
      body: Column(
        children: [
          Container(
            color: const Color(0xFF1E293B),
            padding: const EdgeInsets.all(10),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildChip(552, 'الدوري المصري'),
                _buildChip(572, 'أبطال أفريقيا'),
                _buildChip(573, 'الكونفدرالية'),
              ],
            ),
          ),
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                : scorers.isEmpty
                    ? const Center(child: Text('لا توجد إحصائيات هدافين متاحة حالياً'))
                    : ListView.builder(
                        padding: const EdgeInsets.all(12),
                        itemCount: scorers.length,
                        itemBuilder: (context, index) {
                          final item = scorers[index];
                          final entity = item['entity'] ?? {};
                          final comp = item['competitor'] ?? {};
                          final goals = (item['stats'] as List?)?.isNotEmpty == true
                              ? item['stats'][0]['value']
                              : '0';

                          return Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: const Color(0xFF0F172A),
                                backgroundImage: NetworkImage(AppConstants.playerPhoto(entity['id'] ?? 0)),
                              ),
                              title: Text(entity['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                              subtitle: Text(comp['name'] ?? ''),
                              trailing: Text(
                                '$goals هدف',
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildChip(int id, String label) {
    final bool active = selectedCompId == id;
    return ChoiceChip(
      label: Text(label),
      selected: active,
      selectedColor: const Color(0xFF38BDF8),
      labelStyle: TextStyle(color: active ? Colors.black : Colors.white, fontSize: 12),
      onSelected: (_) {
        setState(() => selectedCompId = id);
        loadScorers();
      },
    );
  }
}
''')

    # 14. نقطة الانطلاق الرئيسية
    write_file("lib/main.dart", r'''
import 'package:flutter/material.dart';
import 'screens/matches_tab.dart';
import 'screens/standings_tab.dart';
import 'screens/scorers_tab.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const EgyptianFootballApp());
}

class EgyptianFootballApp extends StatelessWidget {
  const EgyptianFootballApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'الكرة المصرية',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        cardColor: const Color(0xFF1E293B),
      ),
      home: const Directionality(
        textDirection: TextDirection.rtl,
        child: MainLayoutScreen(),
      ),
    );
  }
}

class MainLayoutScreen extends StatefulWidget {
  const MainLayoutScreen({super.key});

  @override
  State<MainLayoutScreen> createState() => _MainLayoutScreenState();
}

class _MainLayoutScreenState extends State<MainLayoutScreen> {
  int _currentIndex = 0;
  final List<Widget> _screens = const [
    CachedMatchesTab(),
    CachedStandingsTab(),
    CachedScorersTab(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        backgroundColor: const Color(0xFF1E293B),
        selectedItemColor: const Color(0xFF38BDF8),
        unselectedItemColor: Colors.white54,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.sports_soccer), label: 'المباريات'),
          BottomNavigationBarItem(icon: Icon(Icons.leaderboard), label: 'الترتيب'),
          BottomNavigationBarItem(icon: Icon(Icons.emoji_events), label: 'الهدافون'),
        ],
      ),
    );
  }
}
''')

    print("\n🎉 تم تحديث المشروع بالكامل للاعتماد على سيرفر 365Scores الرسمي للموبايل بدون أي مفاتيح!");

if __name__ == "__main__":
    update_365_mobile()