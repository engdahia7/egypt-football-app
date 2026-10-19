import 'package:flutter/material.dart';

class SoccerPitchWidget extends StatelessWidget {
  final Map<String, dynamic> homeComp;
  final Map<String, dynamic> awayComp;

  const SoccerPitchWidget({super.key, required this.homeComp, required this.awayComp});

  @override
  Widget build(BuildContext context) {
    final List<dynamic> homeMembers = homeComp['lineups']?['members'] ?? [];
    final List<dynamic> awayMembers = awayComp['lineups']?['members'] ?? [];

    // status == 1 تعني لاعب أساسي في تشكيل 365Scores
    final List<dynamic> homeStarting = homeMembers.where((m) => m['status'] == 1).toList();
    final List<dynamic> awayStarting = awayMembers.where((m) => m['status'] == 1).toList();

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      height: 620,
      width: double.infinity,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            Positioned.fill(child: CustomPaint(painter: PitchPainter())),
            ..._buildTeamFormation(
              players: homeStarting,
              formationStr: homeComp['lineups']?['formation'] ?? '4-3-3',
              isHome: true,
              shirtColor: const Color(0xFF0284C7),
            ),
            ..._buildTeamFormation(
              players: awayStarting,
              formationStr: awayComp['lineups']?['formation'] ?? '4-3-3',
              isHome: false,
              shirtColor: const Color(0xFFE11D48),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildTeamFormation({
    required List<dynamic> players,
    required String formationStr,
    required bool isHome,
    required Color shirtColor,
  }) {
    if (players.isEmpty) return [];

    // تقسيم التشكيل مثل "4-2-3-1" إلى صفوف: [1 (حارس), 4, 2, 3, 1]
    final List<int> rowsCounts = [1];
    for (var part in formationStr.split('-')) {
      final int? count = int.tryParse(part.trim());
      if (count != null && count > 0) rowsCounts.add(count);
    }
    if (rowsCounts.length == 1) rowsCounts.addAll([4, 4, 2]);

    List<Widget> widgets = [];
    int playerIdx = 0;
    final int totalRows = rowsCounts.length;

    for (int r = 0; r < totalRows; r++) {
      final int colsInThisRow = rowsCounts[r];
      for (int c = 0; c < colsInThisRow; c++) {
        if (playerIdx >= players.length) break;
        final p = players[playerIdx++];

        double xAlign = 0.0;
        if (colsInThisRow > 1) {
          double normX = c / (colsInThisRow - 1);
          if (!isHome) normX = 1.0 - normX;
          xAlign = -0.78 + (normX * 1.56);
        }

        double normY = totalRows > 1 ? r / (totalRows - 1) : 0.0;
        double yAlign = isHome ? -0.90 + (normY * 0.76) : 0.90 - (normY * 0.76);

        final String name = p['athlete']?['name'] ?? p['name'] ?? '';
        final String jersey = '${p['jerseyNumber'] ?? p['formation']?['number'] ?? ''}';

        widgets.add(
          Align(
            alignment: Alignment(xAlign, yAlign),
            child: SizedBox(
              width: 68,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 30,
                    height: 30,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: r == 0 ? Colors.amber.shade700 : shirtColor,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 1.8),
                    ),
                    child: Text(jersey, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
                  ),
                  const SizedBox(height: 2),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                    decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(4)),
                    child: Text(
                      name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 9.5, color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }
    }
    return widgets;
  }
}

class PitchPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    const int stripes = 12;
    final double stripeHeight = size.height / stripes;
    for (int i = 0; i < stripes; i++) {
      canvas.drawRect(
        Rect.fromLTWH(0, i * stripeHeight, size.width, stripeHeight),
        Paint()..color = i.isEven ? const Color(0xFF15803D) : const Color(0xFF166534),
      );
    }
    final Paint linePaint = Paint()
      ..color = Colors.white70
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.6;

    const double pad = 12.0;
    final double w = size.width;
    final double h = size.height;

    canvas.drawRect(Rect.fromLTWH(pad, pad, w - pad * 2, h - pad * 2), linePaint);
    canvas.drawLine(Offset(pad, h / 2), Offset(w - pad, h / 2), linePaint);
    canvas.drawCircle(Offset(w / 2, h / 2), 42, linePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
