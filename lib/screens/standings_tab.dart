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
