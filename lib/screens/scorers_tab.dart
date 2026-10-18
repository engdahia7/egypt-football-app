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
