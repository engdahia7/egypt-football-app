import 'package:flutter/material.dart';
import '../core/football_engine.dart';
import '../widgets/match_card.dart';

class CachedMatchesTab extends StatefulWidget {
  const CachedMatchesTab({super.key});

  @override
  State<CachedMatchesTab> createState() => _CachedMatchesTabState();
}

class _CachedMatchesTabState extends State<CachedMatchesTab> {
  DateTime selectedDate = DateTime(2026, 10, 21);
  bool isLoading = false;
  List<Map<String, dynamic>> matches = [];
  String? selectedFavoriteTeam = "الأهلي";

  @override
  void initState() {
    super.initState();
    loadMatches();
  }

  String formatDate(DateTime d) =>
      "${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}";

  Future<void> loadMatches() async {
    setState(() => isLoading = true);
    final list = await FootballEngine.getMatches(formatDate(selectedDate));
    setState(() {
      matches = list;
      isLoading = false;
    });
  }

  void _chooseFavoriteTeam() {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('اختر فريقك المفضل', style: TextStyle(fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: ['الأهلي', 'الزمالك', 'بيراميدز', 'المصري', 'الاتحاد السكندري', 'الإسماعيلي'].map((name) {
            return ListTile(
              leading: const Icon(Icons.shield, color: Color(0xFF38BDF8)),
              title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              onTap: () {
                setState(() => selectedFavoriteTeam = name);
                Navigator.pop(context);
              },
            );
          }).toList(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('مباريات الكرة المصرية 🇪🇬', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
            onPressed: loadMatches,
          ),
        ],
      ),
      body: Column(
        children: [
          // شريط اختيار التاريخ
          Container(
            padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
            color: const Color(0xFF1E293B),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                IconButton(
                  onPressed: () {
                    setState(() => selectedDate = selectedDate.subtract(const Duration(days: 1)));
                    loadMatches();
                  },
                  icon: const Icon(Icons.arrow_back_ios, size: 18),
                ),
                Text(formatDate(selectedDate),
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF38BDF8))),
                IconButton(
                  onPressed: () {
                    setState(() => selectedDate = selectedDate.add(const Duration(days: 1)));
                    loadMatches();
                  },
                  icon: const Icon(Icons.arrow_forward_ios, size: 18),
                ),
              ],
            ),
          ),

          // شريط الفريق المفضل
          Container(
            margin: const EdgeInsets.all(12),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: Colors.amber.withOpacity(0.5)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.stars, color: Colors.amber, size: 24),
                    const SizedBox(width: 8),
                    Text('الفريق المفضل: $selectedFavoriteTeam',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.amber)),
                  ],
                ),
                TextButton(
                  onPressed: _chooseFavoriteTeam,
                  child: const Text('تغيير', style: TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          ),

          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                : matches.isEmpty
                    ? const Center(child: Text('لا توجد مباريات مسجلة لهذا التاريخ 📅', style: TextStyle(color: Colors.white54)))
                    : ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        itemCount: matches.length,
                        itemBuilder: (context, index) => MatchCard(match: matches[index]),
                      ),
          ),
        ],
      ),
    );
  }
}
