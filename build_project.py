import os

# ضع مفتاح الـ API المجاني الخاص بك هنا بين العلامتين
API_KEY = "81a51f1b684ceae4a9006feb5e06232b"

def write_file(path, content):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✅ تم إنشاء: {path}")

def build():
    print("🚀 جاري بناء ملفات المشروع...")

    # 1. pubspec.yaml
    write_file("pubspec.yaml", r'''
name: egyptian_football_app
description: تطبيق متابعة الفرق والبطولات المصرية
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.2.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0
  shared_preferences: ^2.2.3
  flutter_local_notifications: ^17.2.0
  timezone: ^0.9.2
  share_plus: ^10.0.0
  path_provider: ^2.1.3

dev_dependencies:
  flutter_test:
    sdk: flutter

flutter:
  uses-material-design: true
''')

    # 2. GitHub Actions Workflow
    write_file(".github/workflows/build_apk.yml", r'''
name: Build APK

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
      - name: Create Structure
        run: flutter create --platforms=android --org com.egyptfootball.app .
      - name: Fix Manifest
        run: |
          sed -i 's/<application/<uses-permission android:name="android.permission.INTERNET"\/><uses-permission android:name="android.permission.POST_NOTIFICATIONS"\/><uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM"\/><application/g' android/app/src/main/AndroidManifest.xml
          sed -i 's/android:label="[^"]*"/android:label="الكرة المصرية"/g' android/app/src/main/AndroidManifest.xml
           - name: Enable Desugaring
        run: |
          python3 - <<'PY'
          import re
          from pathlib import Path
          kts = Path("android/app/build.gradle.kts")
          groovy = Path("android/app/build.gradle")
          if kts.exists():
              s = kts.read_text()
              s = re.sub(r"(compileOptions\s*\{)", r"\1\n        isCoreLibraryDesugaringEnabled = true", s, count=1)
              s += '\ndependencies {\n    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")\n}\n'
              kts.write_text(s)
          elif groovy.exists():
              s = groovy.read_text()
              s = re.sub(r"(compileOptions\s*\{)", r"\1\n        coreLibraryDesugaringEnabled true", s, count=1)
              s += "\ndependencies {\n    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.1.4'\n}\n"
              groovy.write_text(s)
          else:
              raise SystemExit("android/app/build.gradle not found")
          PY
      - name: Get Dependencies
        run: flutter pub get
      - name: Build APK
        run: flutter build apk --release --no-tree-shake-icons
      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: Egyptian-Football-APK
          path: build/app/outputs/flutter-apk/app-release.apk
''')

    # 3. app_constants.dart
    write_file("lib/core/app_constants.dart", r'''
class AppConstants {
  static final Set<int> egyptianLeagueIds = {233, 714, 539, 895};
  static final Set<int> egyptianTeamIds = {
    1023, 1040, 1032, 1029, 1030, 1028, 1036, 1039, 1025, 1037, 1041, 1042, 1026, 1570
  };
  static final Map<String, String> arabicNames = {
    'Al Ahly': 'الأهلي',
    'Zamalek SC': 'الزمالك',
    'Pyramids FC': 'بيراميدز',
    'Al Masry': 'المصري البورسعيدي',
    'Al Ittihad': 'الاتحاد السكندري',
    'Ismaily SC': 'الإسماعيلي',
    'Modern Sport': 'مودرن سبورت',
    'Ceramica Cleopatra': 'سيراميكا كليوباترا',
    'Enppi': 'إنبي',
    'Smouha SC': 'سموحة',
    "Tala'ea El Gaish": 'طلائع الجيش',
    'ZED FC': 'زد إف سي',
    'Ghazl El Mahallah': 'غزل المحلة',
    'Egypt': 'منتخب مصر',
    'Premier League': 'الدوري المصري الممتاز',
    'Egypt Cup': 'كأس مصر',
    'CAF Champions League': 'دوري أبطال أفريقيا',
    'CAF Confederation Cup': 'كأس الكونفدرالية الأفريقية',
    'CAF Super Cup': 'السوبر الأفريقي',
  };
  static String translate(String name) => arabicNames[name] ?? name;
}
''')

    # 4. smart_api_cache.dart
    smart_cache_code = r'''
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class SmartApiCache {
  static const String apiKey = '__API_KEY__';

  static Future<Map<String, dynamic>> get({
    required String cacheKey,
    required String url,
    required Duration ttl,
    bool forceRefresh = false,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final String? cachedJson = prefs.getString('data_$cacheKey');
    final int? cachedTime = prefs.getInt('time_$cacheKey');
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
        headers: {'x-apisports-key': apiKey},
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);
        if (data['errors'] == null || (data['errors'] as dynamic).isEmpty) {
          await prefs.setString('data_$cacheKey', response.body);
          await prefs.setInt('time_$cacheKey', now);
        }
        return data;
      } else {
        throw Exception('Error: ${response.statusCode}');
      }
    } catch (e) {
      if (cachedJson != null) {
        return json.decode(cachedJson);
      }
      rethrow;
    }
  }
}
'''.replace("__API_KEY__", API_KEY)
    write_file("lib/core/smart_api_cache.dart", smart_cache_code)

    # 5. notification_service.dart
    write_file("lib/core/notification_service.dart", r'''
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/data/latest_all.dart' as tz;
import 'package:timezone/timezone.dart' as tz;

class NotificationService {
  static final FlutterLocalNotificationsPlugin _notificationsPlugin =
      FlutterLocalNotificationsPlugin();

  static Future<void> init() async {
    tz.initializeTimeZones();
    tz.setLocalLocation(tz.getLocation('Africa/Cairo'));
    const AndroidInitializationSettings initAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    const InitializationSettings initSettings =
        InitializationSettings(android: initAndroid);
    await _notificationsPlugin.initialize(initSettings);
    await _notificationsPlugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.requestNotificationsPermission();
  }

  static Future<void> cancelAllReminders() async {
    await _notificationsPlugin.cancelAll();
  }
}
''')

    # 6. favorite_team.dart
    write_file("lib/models/favorite_team.dart", r'''
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class FavoriteTeam {
  final int id;
  final String name;
  final String logo;
  bool notificationsEnabled;

  FavoriteTeam({
    required this.id,
    required this.name,
    required this.logo,
    this.notificationsEnabled = true,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'logo': logo,
        'notificationsEnabled': notificationsEnabled,
      };

  factory FavoriteTeam.fromJson(Map<String, dynamic> json) => FavoriteTeam(
        id: json['id'],
        name: json['name'],
        logo: json['logo'],
        notificationsEnabled: json['notificationsEnabled'] ?? true,
      );
}

class FavoriteTeamManager {
  static const String _key = 'favorite_team_data';

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

    # 7. favorite_team_banner.dart
    write_file("lib/widgets/favorite_team_banner.dart", r'''
import 'package:flutter/material.dart';
import '../models/favorite_team.dart';

class FavoriteTeamBanner extends StatelessWidget {
  final FavoriteTeam? favoriteTeam;
  final List<dynamic> allMatches;
  final VoidCallback onSelectTeamClicked;
  final VoidCallback onToggleNotifications;
  final String Function(String) translateName;

  const FavoriteTeamBanner({
    super.key,
    required this.favoriteTeam,
    required this.allMatches,
    required this.onSelectTeamClicked,
    required this.onToggleNotifications,
    required this.translateName,
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
      final int homeId = m['teams']['home']['id'];
      final int awayId = m['teams']['away']['id'];
      if (homeId == favoriteTeam!.id || awayId == favoriteTeam!.id) {
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
                  Image.network(favoriteTeam!.logo, width: 24, height: 24),
                  const SizedBox(width: 8),
                  Text('مباريات ${favoriteTeam!.name}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.amber)),
                ],
              ),
              Row(
                children: [
                  IconButton(
                    icon: Icon(
                      favoriteTeam!.notificationsEnabled ? Icons.notifications_active : Icons.notifications_off,
                      color: favoriteTeam!.notificationsEnabled ? const Color(0xFF38BDF8) : Colors.white54,
                      size: 20,
                    ),
                    onPressed: onToggleNotifications,
                    constraints: const BoxConstraints(),
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                  ),
                  GestureDetector(
                    onTap: onSelectTeamClicked,
                    child: const Text('تغيير', style: TextStyle(fontSize: 11, color: Colors.white54)),
                  ),
                ],
              ),
            ],
          ),
          const Divider(height: 16, color: Colors.white12),
          teamMatch == null
              ? const Text('لا توجد مباريات مسجلة لهذا الفريق اليوم 📅',
                  style: TextStyle(fontSize: 12, color: Colors.white60))
              : Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(translateName(teamMatch['teams']['home']['name']),
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        teamMatch['fixture']['status']['short'] == 'NS'
                            ? teamMatch['fixture']['date'].substring(11, 16)
                            : '${teamMatch['goals']['home'] ?? 0} - ${teamMatch['goals']['away'] ?? 0}',
                        style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
                      ),
                    ),
                    Expanded(
                      child: Text(translateName(teamMatch['teams']['away']['name']),
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

  final List<Map<String, dynamic>> egyptianTeamsList = const [
    {'id': 1023, 'name': 'الأهلي', 'logo': 'https://media.api-sports.io/football/teams/1023.png'},
    {'id': 1040, 'name': 'الزمالك', 'logo': 'https://media.api-sports.io/football/teams/1040.png'},
    {'id': 1032, 'name': 'بيراميدز', 'logo': 'https://media.api-sports.io/football/teams/1032.png'},
    {'id': 1029, 'name': 'المصري البورسعيدي', 'logo': 'https://media.api-sports.io/football/teams/1029.png'},
    {'id': 1570, 'name': 'منتخب مصر', 'logo': 'https://media.api-sports.io/football/teams/1570.png'},
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
          itemCount: egyptianTeamsList.length,
          itemBuilder: (context, index) {
            final t = egyptianTeamsList[index];
            return ListTile(
              leading: Image.network(t['logo'], width: 30, height: 30),
              title: Text(t['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
              onTap: () {
                onTeamSelected(FavoriteTeam(id: t['id'], name: t['name'], logo: t['logo']));
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

    # 8. match_card.dart
    write_file("lib/widgets/match_card.dart", r'''
import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../screens/match_details_screen.dart';

class MatchCard extends StatelessWidget {
  final dynamic match;
  const MatchCard({super.key, required this.match});

  @override
  Widget build(BuildContext context) {
    final homeTeam = match['teams']['home'];
    final awayTeam = match['teams']['away'];
    final goals = match['goals'];
    final status = match['fixture']['status'];
    final String shortStatus = status['short'];
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
                    Image.network(homeTeam['logo'], width: 38, height: 38),
                    const SizedBox(height: 6),
                    Text(AppConstants.translate(homeTeam['name']),
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
                    Image.network(awayTeam['logo'], width: 38, height: 38),
                    const SizedBox(height: 6),
                    Text(AppConstants.translate(awayTeam['name']),
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

    # 9. soccer_pitch_widget.dart
    write_file("lib/widgets/soccer_pitch_widget.dart", r'''
import 'package:flutter/material.dart';

class SoccerPitchWidget extends StatelessWidget {
  final Map<String, dynamic> homeLineup;
  final Map<String, dynamic> awayLineup;

  const SoccerPitchWidget({super.key, required this.homeLineup, required this.awayLineup});

  @override
  Widget build(BuildContext context) {
    final List<dynamic> homeXI = homeLineup['startXI'] ?? [];
    final List<dynamic> awayXI = awayLineup['startXI'] ?? [];

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      height: 640,
      width: double.infinity,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            Positioned.fill(child: CustomPaint(painter: PitchPainter())),
            ..._buildTeamNodes(players: homeXI, isHome: true, shirtColor: const Color(0xFF0284C7)),
            ..._buildTeamNodes(players: awayXI, isHome: false, shirtColor: const Color(0xFFE11D48)),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildTeamNodes({required List<dynamic> players, required bool isHome, required Color shirtColor}) {
    int maxRow = 1;
    final Map<int, int> maxColInRow = {};

    for (var item in players) {
      final String? grid = item['player']['grid'];
      if (grid != null && grid.contains(':')) {
        final parts = grid.split(':');
        final int r = int.tryParse(parts[0]) ?? 1;
        final int c = int.tryParse(parts[1]) ?? 1;
        if (r > maxRow) maxRow = r;
        if (c > (maxColInRow[r] ?? 0)) maxColInRow[r] = c;
      }
    }

    List<Widget> widgets = [];
    for (var i = 0; i < players.length; i++) {
      final player = players[i]['player'];
      final String? grid = player['grid'];
      int row = 1, col = 1;

      if (grid != null && grid.contains(':')) {
        final parts = grid.split(':');
        row = int.tryParse(parts[0]) ?? 1;
        col = int.tryParse(parts[1]) ?? 1;
      } else {
        if (i == 0) { row = 1; col = 1; }
        else if (i <= 4) { row = 2; col = i; maxColInRow[2] = 4; }
        else if (i <= 8) { row = 3; col = i - 4; maxColInRow[3] = 4; }
        else { row = 4; col = i - 8; maxColInRow[4] = 2; }
        maxRow = 4;
      }

      final int totalCols = maxColInRow[row] ?? 1;
      double xAlign = 0.0;
      if (totalCols > 1) {
        double normalizedX = (col - 1) / (totalCols - 1);
        if (!isHome) normalizedX = 1.0 - normalizedX;
        xAlign = -0.78 + (normalizedX * 1.56);
      }

      double normalizedY = maxRow > 1 ? (row - 1) / (maxRow - 1) : 0.0;
      double yAlign = isHome ? -0.91 + (normalizedY * 0.77) : 0.91 - (normalizedY * 0.77);

      final String fullName = player['name'] ?? '';
      final String shortName = fullName.split(' ').last;

      widgets.add(
        Align(
          alignment: Alignment(xAlign, yAlign),
          child: SizedBox(
            width: 66,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 30,
                  height: 30,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: row == 1 ? Colors.amber.shade700 : shirtColor,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 1.8),
                  ),
                  child: Text('${player['number'] ?? 0}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
                ),
                const SizedBox(height: 2),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                  decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(4)),
                  child: Text(shortName, maxLines: 1, overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 10, color: Colors.white)),
                ),
              ],
            ),
          ),
        ),
      );
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

    # 10. share_card_helper.dart
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
                  Text('تابع فريقك لحظة بلحظة 📲', style: TextStyle(fontSize: 10, color: Color(0xFF38BDF8))),
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

    # 11. matches_tab.dart
    write_file("lib/screens/matches_tab.dart", r'''
import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../core/smart_api_cache.dart';
import '../core/notification_service.dart';
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
    setState(() => isLoading = true);
    final String dateStr = formatDate(selectedDate);
    try {
      final data = await SmartApiCache.get(
        cacheKey: 'matches_$dateStr',
        url: 'https://v3.football.api-sports.io/fixtures?date=$dateStr&timezone=Africa/Cairo',
        ttl: const Duration(minutes: 15),
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
    } catch (_) {
      setState(() => isLoading = false);
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

  void _toggleNotifications() async {
    if (favoriteTeam != null) {
      setState(() {
        favoriteTeam!.notificationsEnabled = !favoriteTeam!.notificationsEnabled;
      });
      await FavoriteTeamManager.saveFavorite(favoriteTeam!);
      if (!favoriteTeam!.notificationsEnabled) {
        await NotificationService.cancelAllReminders();
      }
    }
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
          FavoriteTeamBanner(
            favoriteTeam: favoriteTeam,
            allMatches: filteredMatches,
            onSelectTeamClicked: _openTeamSelector,
            onToggleNotifications: _toggleNotifications,
            translateName: AppConstants.translate,
          ),
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                : filteredMatches.isEmpty
                    ? const Center(child: Text('لا توجد مباريات للفرق المصرية في هذا اليوم', style: TextStyle(color: Colors.white54)))
                    : ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        itemCount: filteredMatches.length,
                        itemBuilder: (context, index) => MatchCard(match: filteredMatches[index]),
                      ),
          ),
        ],
      ),
    );
  }
}
''')

    # 12. match_details_screen.dart
    write_file("lib/screens/match_details_screen.dart", r'''
import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../core/smart_api_cache.dart';
import '../widgets/soccer_pitch_widget.dart';
import '../widgets/share_card_helper.dart';

class MatchDetailsScreen extends StatefulWidget {
  final int fixtureId;
  const MatchDetailsScreen({super.key, required this.fixtureId});

  @override
  State<MatchDetailsScreen> createState() => _MatchDetailsScreenState();
}

class _MatchDetailsScreenState extends State<MatchDetailsScreen> {
  bool isLoading = true;
  Map<String, dynamic>? matchData;
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
        cacheKey: 'fixture_${widget.fixtureId}',
        url: 'https://v3.football.api-sports.io/fixtures?id=${widget.fixtureId}',
        ttl: const Duration(minutes: 5),
        forceRefresh: forceRefresh,
      );
      final List<dynamic> list = data['response'] ?? [];
      setState(() {
        matchData = list.isNotEmpty ? list.first : null;
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
          title: const Text('تفاصيل المباراة', style: TextStyle(fontSize: 17)),
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
              Tab(text: 'المجريات ⏱️'),
              Tab(text: 'التشكيل 👕'),
              Tab(text: 'الإحصائيات 📊'),
            ],
          ),
        ),
        body: isLoading || matchData == null
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
    final home = matchData!['teams']['home'];
    final away = matchData!['teams']['away'];
    final goals = matchData!['goals'];
    return Container(
      padding: const EdgeInsets.all(16),
      color: const Color(0xFF1E293B),
      child: Row(
        children: [
          Expanded(
            child: Column(
              children: [
                Image.network(home['logo'], width: 48, height: 48),
                const SizedBox(height: 6),
                Text(AppConstants.translate(home['name']),
                    textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
          ),
          Text('${goals['home'] ?? '-'} : ${goals['away'] ?? '-'}',
              style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
          Expanded(
            child: Column(
              children: [
                Image.network(away['logo'], width: 48, height: 48),
                const SizedBox(height: 6),
                Text(AppConstants.translate(away['name']),
                    textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEventsTab() {
    final List<dynamic> events = matchData!['events'] ?? [];
    if (events.isEmpty) return const Center(child: Text('لا توجد أحداث مسجلة بعد'));
    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: events.length,
      itemBuilder: (context, index) {
        final e = events[index];
        final String type = e['type'] ?? '';
        final String icon = type == 'Goal' ? '⚽' : (type == 'Card' ? '🟨' : (type == 'subst' ? '🔄' : '📌'));
        return Card(
          child: ListTile(
            leading: Text("${e['time']['elapsed']}'",
                style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold)),
            title: Text('$icon ${e['player']['name'] ?? ''}'),
            subtitle: Text(AppConstants.translate(e['team']['name'] ?? '')),
          ),
        );
      },
    );
  }

  Widget _buildLineupsTab() {
    final List<dynamic> lineups = matchData!['lineups'] ?? [];
    if (lineups.length < 2) return const Center(child: Text('يصدر التشكيل الرسمي قبل المباراة بـ 45 دقيقة'));
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
          child: SoccerPitchWidget(homeLineup: lineups[0], awayLineup: lineups[1]),
        ),
      ],
    );
  }

  Widget _buildStatsTab() {
    final List<dynamic> stats = matchData!['statistics'] ?? [];
    if (stats.length < 2) return const Center(child: Text('لا تتوفر إحصائيات حالياً'));
    final List<dynamic> homeStats = stats[0]['statistics'] ?? [];
    final List<dynamic> awayStats = stats[1]['statistics'] ?? [];
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: homeStats.length,
      itemBuilder: (context, index) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('${homeStats[index]['value'] ?? 0}', style: const TextStyle(fontWeight: FontWeight.bold)),
              Text('${homeStats[index]['type']}', style: const TextStyle(color: Colors.white60)),
              Text('${awayStats[index]['value'] ?? 0}', style: const TextStyle(fontWeight: FontWeight.bold)),
            ],
          ),
        );
      },
    );
  }
}
''')

    # 13. standings_tab.dart
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
  int selectedLeagueId = 233;
  int selectedSeason = 2025;
  bool isLoading = false;
  List<dynamic> groups = [];

  @override
  void initState() {
    super.initState();
    loadStandings();
  }

  Future<void> loadStandings({bool forceRefresh = false}) async {
    setState(() => isLoading = true);
    try {
      final data = await SmartApiCache.get(
        cacheKey: 'standings_${selectedLeagueId}_$selectedSeason',
        url: 'https://v3.football.api-sports.io/standings?league=$selectedLeagueId&season=$selectedSeason',
        ttl: const Duration(hours: 6),
        forceRefresh: forceRefresh,
      );
      final List<dynamic> res = data['response'] ?? [];
      setState(() {
        groups = res.isNotEmpty ? (res.first['league']['standings'] ?? []) : [];
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
        title: const Text('جدول الترتيب والمجموعات 🏆', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
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
                _buildChip(233, 'الدوري المصري'),
                _buildChip(12, 'أبطال أفريقيا'),
                _buildChip(20, 'الكونفدرالية'),
              ],
            ),
          ),
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                : groups.isEmpty
                    ? const Center(child: Text('لا توجد جداول متاحة حالياً'))
                    : ListView.builder(
                        padding: const EdgeInsets.all(12),
                        itemCount: groups.length,
                        itemBuilder: (context, gIndex) {
                          final List<dynamic> table = groups[gIndex];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 16),
                            child: Column(
                              children: table.map((row) {
                                return ListTile(
                                  dense: true,
                                  leading: Text('${row['rank']}', style: const TextStyle(fontWeight: FontWeight.bold)),
                                  title: Row(
                                    children: [
                                      Image.network(row['team']['logo'], width: 22, height: 22),
                                      const SizedBox(width: 8),
                                      Expanded(child: Text(AppConstants.translate(row['team']['name']))),
                                    ],
                                  ),
                                  trailing: Text(
                                    '${row['points']} نقطة (لعب ${row['all']['played']})',
                                    style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold),
                                  ),
                                );
                              }).toList(),
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
    final bool active = selectedLeagueId == id;
    return ChoiceChip(
      label: Text(label),
      selected: active,
      selectedColor: const Color(0xFF38BDF8),
      labelStyle: TextStyle(color: active ? Colors.black : Colors.white, fontSize: 12),
      onSelected: (_) {
        setState(() => selectedLeagueId = id);
        loadStandings();
      },
    );
  }
}
''')

    # 14. scorers_tab.dart
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
  int selectedLeagueId = 233;
  int selectedSeason = 2025;
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
        cacheKey: 'scorers_${selectedLeagueId}_$selectedSeason',
        url: 'https://v3.football.api-sports.io/players/topscorers?league=$selectedLeagueId&season=$selectedSeason',
        ttl: const Duration(hours: 6),
        forceRefresh: forceRefresh,
      );
      setState(() {
        scorers = data['response'] ?? [];
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
      body: isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
          : scorers.isEmpty
              ? const Center(child: Text('لا توجد بيانات هدافين متاحة'))
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: scorers.length,
                  itemBuilder: (context, index) {
                    final item = scorers[index];
                    final player = item['player'];
                    final stats = (item['statistics'] as List).first;
                    final goals = stats['goals']['total'] ?? 0;

                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundImage: NetworkImage(player['photo'] ?? ''),
                        ),
                        title: Text(player['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text(AppConstants.translate(stats['team']['name'])),
                        trailing: Text(
                          '$goals هدف',
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

    # 15. main.dart
    write_file("lib/main.dart", r'''
import 'package:flutter/material.dart';
import 'core/notification_service.dart';
import 'screens/matches_tab.dart';
import 'screens/standings_tab.dart';
import 'screens/scorers_tab.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await NotificationService.init();
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

    print("\n🎉 تم إنشاء جميع الملفات بنجاح تام بدون أي أخطاء!")

if __name__ == "__main__":
    build()
