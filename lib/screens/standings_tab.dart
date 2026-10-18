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
