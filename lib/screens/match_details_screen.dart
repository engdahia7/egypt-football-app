import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';

class MatchDetailsScreen extends StatelessWidget {
  final Map<String, dynamic> match;
  const MatchDetailsScreen({super.key, required this.match});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: Text(match['league'] ?? 'تفاصيل المباراة', style: const TextStyle(fontSize: 16)),
        actions: [
          IconButton(
            icon: const Icon(Icons.share, color: Colors.greenAccent),
            onPressed: () {
              Share.share('⚽ مباراة: ${match['home']} ضد ${match['away']}\n⏰ الموعد: ${match['time']}\n📺 القناة: ${match['tv']}\nعبر تطبيق الكرة المصرية 🇪🇬');
            },
          )
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(color: const Color(0xFF1E293B), borderRadius: BorderRadius.circular(16)),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Column(
                  children: [
                    Image.network(match['home_logo'], width: 52, height: 52, errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 48)),
                    const SizedBox(height: 8),
                    Text(match['home'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  ],
                ),
                Text(
                  match['home_score'] != null ? '${match['home_score']} : ${match['away_score']}' : match['time'],
                  style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
                ),
                Column(
                  children: [
                    Image.network(match['away_logo'], width: 52, height: 52, errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 48)),
                    const SizedBox(height: 8),
                    Text(match['away'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: ListTile(
              leading: const Icon(Icons.tv, color: Colors.amber),
              title: const Text('القناة الناقلة'),
              subtitle: Text(match['tv'] ?? 'أون تايم سبورتس HD', style: const TextStyle(fontWeight: FontWeight.bold)),
            ),
          ),
          Card(
            child: ListTile(
              leading: const Icon(Icons.stadium, color: Color(0xFF38BDF8)),
              title: const Text('الملعب'),
              subtitle: const Text('ستاد القاهرة الدولي', style: TextStyle(fontWeight: FontWeight.bold)),
            ),
          ),
        ],
      ),
    );
  }
}
