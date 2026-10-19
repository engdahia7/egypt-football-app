import 'package:flutter/material.dart';
import '../models/favorite_team.dart';

class FavoriteTeamBanner extends StatelessWidget {
  final FavoriteTeam? favoriteTeam;
  final List<dynamic> allMatches;
  final VoidCallback onSelectTeamClicked;

  const FavoriteTeamBanner({
    super.key,
    required this.favoriteTeam,
    required this.allMatches,
    required this.onSelectTeamClicked,
  });

  @override
  Widget build(BuildContext context) {
    if (favoriteTeam == null) {
      return Container(
        margin: const EdgeInsets.all(12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFF38BDF8).withOpacity(0.3)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Row(
              children: [
                Icon(Icons.star, color: Colors.amber, size: 22),
                SizedBox(width: 10),
                Text('اختر فريقك المفضل لمتابعة مبارياته',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
              ],
            ),
            TextButton(
              onPressed: onSelectTeamClicked,
              child: const Text('اختيار',
                  style: TextStyle(color: Color(0xFF38BDF8), fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      );
    }

    dynamic teamMatch;
    for (var m in allMatches) {
      final String hName = m['homeCompetitor']?['name'] ?? '';
      final String aName = m['awayCompetitor']?['name'] ?? '';
      if (hName.contains(favoriteTeam!.name) || aName.contains(favoriteTeam!.name)) {
        teamMatch = m;
        break;
      }
    }

    return Container(
      margin: const EdgeInsets.all(12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [Color(0xFF1E293B), Color(0xFF0F172A)]),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.amber.withOpacity(0.4), width: 1.2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.stars, color: Colors.amber, size: 22),
                  const SizedBox(width: 8),
                  Text('فريقي المفضل: ${favoriteTeam!.name}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.amber)),
                ],
              ),
              GestureDetector(
                onTap: onSelectTeamClicked,
                child: const Text('تغيير الفريق', style: TextStyle(fontSize: 12, color: Color(0xFF38BDF8))),
              ),
            ],
          ),
          const Divider(height: 16, color: Colors.white12),
          teamMatch == null
              ? const Text('لا توجد مباراة مسجلة لفريقك في هذا التاريخ 📅',
                  style: TextStyle(fontSize: 12, color: Colors.white60))
              : Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(teamMatch['homeCompetitor']['name'] ?? '',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        teamMatch['statusGroup'] == 2
                            ? (teamMatch['startTime'] ?? '').toString().substring(11, 16)
                            : '${teamMatch['homeCompetitor']['score'] ?? 0} - ${teamMatch['awayCompetitor']['score'] ?? 0}',
                        style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
                      ),
                    ),
                    Expanded(
                      child: Text(teamMatch['awayCompetitor']['name'] ?? '',
                          textAlign: TextAlign.left,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    ),
                  ],
                ),
        ],
      ),
    );
  }
}

class SelectFavoriteTeamDialog extends StatelessWidget {
  final Function(FavoriteTeam) onTeamSelected;
  const SelectFavoriteTeamDialog({super.key, required this.onTeamSelected});

  final List<String> egyptianTeams = const [
    'الأهلي',
    'الزمالك',
    'بيراميدز',
    'المصري',
    'الاتحاد السكندري',
    'الإسماعيلي',
    'سيراميكا كليوباترا',
    'مودرن سبورت',
    'سموحة',
    'إنبي',
    'غزل المحلة',
    'زد',
    'مصر',
  ];

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: const Color(0xFF1E293B),
      title: const Text('اختر فريقك المفضل', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
      content: SizedBox(
        width: double.maxFinite,
        child: ListView.builder(
          shrinkWrap: true,
          itemCount: egyptianTeams.length,
          itemBuilder: (context, index) {
            final name = egyptianTeams[index];
            return ListTile(
              leading: const Icon(Icons.shield, color: Color(0xFF38BDF8)),
              title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold)),
              onTap: () {
                onTeamSelected(FavoriteTeam(name: name, logo: ''));
                Navigator.pop(context);
              },
            );
          },
        ),
      ),
    );
  }
}
