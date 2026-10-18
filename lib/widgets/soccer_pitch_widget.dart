import 'package:flutter/material.dart';

class SoccerPitchWidget extends StatelessWidget {
  final Map<String, dynamic> homeLineup;
  final Map<String, dynamic> awayLineup;

  const SoccerPitchWidget({super.key, required this.homeLineup, required this.awayLineup});

  @override
  Widget build(BuildContext context) {
    final List<dynamic> homeXI = homeLineup['startXI'] ?? [];
    final List<dynamic> awayXI = awayLineup['startXI'] ?? [];

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      height: 640,
      width: double.infinity,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(16),
        child: Stack(
          children: [
            Positioned.fill(child: CustomPaint(painter: PitchPainter())),
            ..._buildTeamNodes(players: homeXI, isHome: true, shirtColor: const Color(0xFF0284C7)),
            ..._buildTeamNodes(players: awayXI, isHome: false, shirtColor: const Color(0xFFE11D48)),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildTeamNodes({required List<dynamic> players, required bool isHome, required Color shirtColor}) {
    int maxRow = 1;
    final Map<int, int> maxColInRow = {};

    for (var item in players) {
      final String? grid = item['player']['grid'];
      if (grid != null && grid.contains(':')) {
        final parts = grid.split(':');
        final int r = int.tryParse(parts[0]) ?? 1;
        final int c = int.tryParse(parts[1]) ?? 1;
        if (r > maxRow) maxRow = r;
        if (c > (maxColInRow[r] ?? 0)) maxColInRow[r] = c;
      }
    }

    List<Widget> widgets = [];
    for (var i = 0; i < players.length; i++) {
      final player = players[i]['player'];
      final String? grid = player['grid'];
      int row = 1, col = 1;

      if (grid != null && grid.contains(':')) {
        final parts = grid.split(':');
        row = int.tryParse(parts[0]) ?? 1;
        col = int.tryParse(parts[1]) ?? 1;
      } else {
        if (i == 0) { row = 1; col = 1; }
        else if (i <= 4) { row = 2; col = i; maxColInRow[2] = 4; }
        else if (i <= 8) { row = 3; col = i - 4; maxColInRow[3] = 4; }
        else { row = 4; col = i - 8; maxColInRow[4] = 2; }
        maxRow = 4;
      }

      final int totalCols = maxColInRow[row] ?? 1;
      double xAlign = 0.0;
      if (totalCols > 1) {
        double normalizedX = (col - 1) / (totalCols - 1);
        if (!isHome) normalizedX = 1.0 - normalizedX;
        xAlign = -0.78 + (normalizedX * 1.56);
      }

      double normalizedY = maxRow > 1 ? (row - 1) / (maxRow - 1) : 0.0;
      double yAlign = isHome ? -0.91 + (normalizedY * 0.77) : 0.91 - (normalizedY * 0.77);

      final String fullName = player['name'] ?? '';
      final String shortName = fullName.split(' ').last;

      widgets.add(
        Align(
          alignment: Alignment(xAlign, yAlign),
          child: SizedBox(
            width: 66,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 30,
                  height: 30,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: row == 1 ? Colors.amber.shade700 : shirtColor,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 1.8),
                  ),
                  child: Text('${player['number'] ?? 0}',
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
                ),
                const SizedBox(height: 2),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                  decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(4)),
                  child: Text(shortName, maxLines: 1, overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 10, color: Colors.white)),
                ),
              ],
            ),
          ),
        ),
      );
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
