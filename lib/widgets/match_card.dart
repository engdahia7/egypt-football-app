import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../screens/match_details_screen.dart';

class MatchCard extends StatelessWidget {
  final dynamic match;
  const MatchCard({super.key, required this.match});

  @override
  Widget build(BuildContext context) {
    final home = match['teams']['home'];
    final away = match['teams']['away'];
    final goals = match['goals'];
    final status = match['fixture']['status'];
    final String shortStatus = status['short'] ?? 'NS';
    final int? elapsed = status['elapsed'];
    final String matchTime = match['fixture']['date'].substring(11, 16);

    final bool isLive = ['1H', '2H', 'HT', 'ET', 'P'].contains(shortStatus);
    final bool isFinished = ['FT', 'AET', 'PEN'].contains(shortStatus);

    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => Directionality(
              textDirection: TextDirection.rtl,
              child: MatchDetailsScreen(fixtureId: match['fixture']['id']),
            ),
          ),
        );
      },
      child: Card(
        margin: const EdgeInsets.only(bottom: 10),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  children: [
                    Image.network(home['logo'], width: 38, height: 38,
                        errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 36)),
                    const SizedBox(height: 6),
                    Text(AppConstants.translate(home['name']),
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    Text(
                      (isLive || isFinished)
                          ? '${goals['home'] ?? 0}  -  ${goals['away'] ?? 0}'
                          : matchTime,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: (isLive || isFinished) ? Colors.white : const Color(0xFF38BDF8),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      isLive ? 'مباشر $elapsed\'' : (isFinished ? 'انتهت' : 'لم تبدأ'),
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
                    Image.network(away['logo'], width: 38, height: 38,
                        errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 36)),
                    const SizedBox(height: 6),
                    Text(AppConstants.translate(away['name']),
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
