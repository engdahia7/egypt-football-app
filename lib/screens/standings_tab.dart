import 'package:flutter/material.dart';
import '../core/football_engine.dart';

class CachedStandingsTab extends StatelessWidget {
  const CachedStandingsTab({super.key});

  @override
  Widget build(BuildContext context) {
    final list = FootballEngine.standings;
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('جدول ترتيب الدوري المصري 🏆', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: list.length,
        itemBuilder: (context, index) {
          final row = list[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 6),
            child: ListTile(
              dense: true,
              leading: Text('${row['rank']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
              title: Row(
                children: [
                  Image.network(row['logo'], width: 26, height: 26, errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 22)),
                  const SizedBox(width: 10),
                  Text(row['team'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
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
