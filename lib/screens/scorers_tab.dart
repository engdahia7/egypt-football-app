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
        cacheKey: '365_scorers_$selectedCompId',
        url: 'https://webws.365scores.com/web/stats/?appTypeId=5&langId=27&timezoneName=Africa/Cairo&userCountryId=131&competitions=$selectedCompId',
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
