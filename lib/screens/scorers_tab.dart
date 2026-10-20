import 'package:flutter/material.dart';
import '../core/football_engine.dart';

class CachedScorersTab extends StatefulWidget {
  const CachedScorersTab({super.key});

  @override
  State<CachedScorersTab> createState() => _CachedScorersTabState();
}

class _CachedScorersTabState extends State<CachedScorersTab> {
  bool isLoading = true;
  List<Map<String, dynamic>> scorers = [];

  @override
  void initState() {
    super.initState();
    loadScorers();
  }

  Future<void> loadScorers() async {
    setState(() => isLoading = true);
    final data = await FootballEngine.getScorers();
    setState(() {
      scorers = data;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('قائمة الهدافين 👟⚽', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
        actions: [
          IconButton(icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)), onPressed: loadScorers),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
          : scorers.isEmpty
              ? const Center(child: Text('جاري تحديث إحصائيات الهدافين...', style: TextStyle(color: Colors.white54)))
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: scorers.length,
                  itemBuilder: (context, index) {
                    final s = scorers[index];
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
