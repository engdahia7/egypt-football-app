import 'package:flutter/material.dart';
import '../models/favorite_team.dart';

class FavoriteTeamBanner extends StatelessWidget {
  final FavoriteTeam? favoriteTeam;
  final List<dynamic> allMatches;
  final VoidCallback onSelectTeamClicked;
  final VoidCallback onToggleNotifications;
  final String Function(String) translateName;

  const FavoriteTeamBanner({
    super.key,
    required this.favoriteTeam,
    required this.allMatches,
    required this.onSelectTeamClicked,
    required this.onToggleNotifications,
    required this.translateName,
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
      final int homeId = m['teams']['home']['id'];
      final int awayId = m['teams']['away']['id'];
      if (homeId == favoriteTeam!.id || awayId == favoriteTeam!.id) {
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
                  Image.network(favoriteTeam!.logo, width: 24, height: 24),
                  const SizedBox(width: 8),
                  Text('مباريات ${favoriteTeam!.name}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Colors.amber)),
                ],
              ),
              Row(
                children: [
                  IconButton(
                    icon: Icon(
                      favoriteTeam!.notificationsEnabled ? Icons.notifications_active : Icons.notifications_off,
                      color: favoriteTeam!.notificationsEnabled ? const Color(0xFF38BDF8) : Colors.white54,
                      size: 20,
                    ),
                    onPressed: onToggleNotifications,
                    constraints: const BoxConstraints(),
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                  ),
                  GestureDetector(
                    onTap: onSelectTeamClicked,
                    child: const Text('تغيير', style: TextStyle(fontSize: 11, color: Colors.white54)),
                  ),
                ],
              ),
            ],
          ),
          const Divider(height: 16, color: Colors.white12),
          teamMatch == null
              ? const Text('لا توجد مباريات مسجلة لهذا الفريق اليوم 📅',
                  style: TextStyle(fontSize: 12, color: Colors.white60))
              : Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(translateName(teamMatch['teams']['home']['name']),
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        teamMatch['fixture']['status']['short'] == 'NS'
                            ? teamMatch['fixture']['date'].substring(11, 16)
                            : '${teamMatch['goals']['home'] ?? 0} - ${teamMatch['goals']['away'] ?? 0}',
                        style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF38BDF8)),
                      ),
                    ),
                    Expanded(
                      child: Text(translateName(teamMatch['teams']['away']['name']),
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

  final List<Map<String, dynamic>> egyptianTeamsList = const [
    {'id': 1023, 'name': 'الأهلي', 'logo': 'https://media.api-sports.io/football/teams/1023.png'},
    {'id': 1040, 'name': 'الزمالك', 'logo': 'https://media.api-sports.io/football/teams/1040.png'},
    {'id': 1032, 'name': 'بيراميدز', 'logo': 'https://media.api-sports.io/football/teams/1032.png'},
    {'id': 1029, 'name': 'المصري البورسعيدي', 'logo': 'https://media.api-sports.io/football/teams/1029.png'},
    {'id': 1570, 'name': 'منتخب مصر', 'logo': 'https://media.api-sports.io/football/teams/1570.png'},
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
          itemCount: egyptianTeamsList.length,
          itemBuilder: (context, index) {
            final t = egyptianTeamsList[index];
            return ListTile(
              leading: Image.network(t['logo'], width: 30, height: 30),
              title: Text(t['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
              onTap: () {
                onTeamSelected(FavoriteTeam(id: t['id'], name: t['name'], logo: t['logo']));
                Navigator.pop(context);
              },
            );
          },
        ),
      ),
    );
  }
}
