import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../screens/match_details_screen.dart';

class MatchCard extends StatelessWidget {
  final dynamic match;
  const MatchCard({super.key, required this.match});

  @override
  Widget build(BuildContext context) {
    final home = match['homeCompetitor'] ?? {};
    final away = match['awayCompetitor'] ?? {};
    final int homeId = home['id'] ?? 0;
    final int awayId = away['id'] ?? 0;
    final int homeScore = (home['score'] ?? -1).toInt();
    final int awayScore = (away['score'] ?? -1).toInt();

    // statusGroup: 2 = لم تبدأ | 3 = جارية الآن (مباشر) | 4 = انتهت
    final int statusGroup = match['statusGroup'] ?? 2;
    final String statusText = match['statusText'] ?? '';
    final String compName = match['competitionDisplayName'] ?? '';
    final String startTimeStr = match['startTime'] ?? '';
    final String timeOnly = startTimeStr.length >= 16 ? startTimeStr.substring(11, 16) : '';

    final bool isLive = statusGroup == 3;
    final bool isFinished = statusGroup == 4;
    final bool hasScore = homeScore >= 0 && awayScore >= 0;

    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => Directionality(
              textDirection: TextDirection.rtl,
              child: MatchDetailsScreen(gameId: match['id']),
            ),
          ),
        );
      },
      child: Card(
        margin: const EdgeInsets.only(bottom: 10),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
          child: Column(
            children: [
              // اسم البطولة في أعلى الكارت
              Text(
                compName,
                style: const TextStyle(fontSize: 11, color: Colors.amber, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: Column(
                      children: [
                        Image.network(
                          AppConstants.teamLogo(homeId),
                          width: 38,
                          height: 38,
                          errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 36),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          home['name'] ?? '',
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                        ),
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
                          hasScore ? '$homeScore  -  $awayScore' : timeOnly,
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: hasScore ? Colors.white : const Color(0xFF38BDF8),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          isLive ? '🔴 $statusText (${match['gameTimeDisplay'] ?? ''})' : statusText,
                          style: TextStyle(
                            fontSize: 11,
                            color: isLive
                                ? Colors.redAccent
                                : (isFinished ? Colors.greenAccent : Colors.white54),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child: Column(
                      children: [
                        Image.network(
                          AppConstants.teamLogo(awayId),
                          width: 38,
                          height: 38,
                          errorBuilder: (_, __, ___) => const Icon(Icons.shield, size: 36),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          away['name'] ?? '',
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                        ),
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
