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
        cacheKey: '365_game_${widget.gameId}',
        url: 'https://webws.365scores.com/web/game/?appTypeId=5&langId=27&timezoneName=Africa/Cairo&userCountryId=131&gameId=${widget.gameId}',
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
