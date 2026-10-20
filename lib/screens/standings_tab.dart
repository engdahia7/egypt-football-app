import 'package:flutter/material.dart';
import '../core/football_engine.dart';

class CachedStandingsTab extends StatefulWidget {
  const CachedStandingsTab({super.key});

  @override
  State<CachedStandingsTab> createState() => _CachedStandingsTabState();
}

class _CachedStandingsTabState extends State<CachedStandingsTab> {
  bool isLoading = true;
  List<Map<String, dynamic>> table = [];

  @override
  void initState() {
    super.initState();
    loadStandings();
  }

  Future<void> loadStandings() async {
    setState(() => isLoading = true);
    final data = await FootballEngine.getStandings();
    setState(() {
      table = data;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('جدول ترتيب الدوري المصري 🏆', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
        actions: [
          IconButton(icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)), onPressed: loadStandings),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
          : table.isEmpty
              ? const Center(child: Text('جاري تحديث جدول الترتيب مع بداية الجولة...', style: TextStyle(color: Colors.white54)))
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: table.length,
                  itemBuilder: (context, index) {
                    final row = table[index];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 6),
                      child: ListTile(
                        dense: true,
                        leading: Text('${row['rank']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                        title: Row(
                          children: [
                            Image.network(row['logo'], width: 26, height: 26, errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 22)),
                            const SizedBox(width: 10),
                            Expanded(child: Text(row['team'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14))),
                          ],
                        ),
                        trailing: Text(
                          '${row['points']} نقطة (لعب ${row['played']})',
                          style: const TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
