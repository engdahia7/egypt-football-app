import 'package:flutter/material.dart';
import '../screens/match_details_screen.dart';

class MatchCard extends StatelessWidget {
  final Map<String, dynamic> match;
  const MatchCard({super.key, required this.match});

  @override
  Widget build(BuildContext context) {
    final bool isLive = match['status'] == 'مباشر';
    final bool isFinished = match['status'] == 'انتهت';
    final hasScore = match['home_score'] != null;

    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => Directionality(
              textDirection: TextDirection.rtl,
              child: MatchDetailsScreen(match: match),
            ),
          ),
        );
      },
      child: Card(
        margin: const EdgeInsets.only(bottom: 10),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
          child: Column(
            children: [
              Text(match['league'] ?? '', style: const TextStyle(fontSize: 11, color: Colors.amber, fontWeight: FontWeight.w600)),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: Column(
                      children: [
                        Image.network(match['home_logo'], width: 38, height: 38, errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 36)),
                        const SizedBox(height: 6),
                        Text(match['home'], textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    decoration: BoxDecoration(color: const Color(0xFF0F172A), borderRadius: BorderRadius.circular(12)),
                    child: Column(
                      children: [
                        Text(
                          hasScore ? '${match['home_score']}  -  ${match['away_score']}' : match['time'],
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: hasScore ? Colors.white : const Color(0xFF38BDF8)),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          match['status'],
                          style: TextStyle(
                            fontSize: 11,
                            color: isLive ? Colors.redAccent : (isFinished ? Colors.greenAccent : Colors.white54),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: Column(
                      children: [
                        Image.network(match['away_logo'], width: 38, height: 38, errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 36)),
                        const SizedBox(height: 6),
                        Text(match['away'], textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
