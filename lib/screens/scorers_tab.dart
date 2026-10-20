import 'package:flutter/material.dart';
import '../core/football_engine.dart';

class CachedScorersTab extends StatelessWidget {
  const CachedScorersTab({super.key});

  @override
  Widget build(BuildContext context) {
    final list = FootballEngine.topScorers;
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('قائمة الهدافين 👟⚽', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: list.length,
        itemBuilder: (context, index) {
          final s = list[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: const Color(0xFF0F172A),
                backgroundImage: NetworkImage(s['photo']),
              ),
              title: Text(s['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text(s['team']),
              trailing: Text(
                '${s['goals']} أهداف',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
              ),
            ),
          );
        },
      ),
    );
  }
}
