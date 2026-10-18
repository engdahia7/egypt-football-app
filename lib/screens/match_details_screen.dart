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
