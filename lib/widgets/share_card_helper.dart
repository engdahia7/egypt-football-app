import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class ShareableMatchWidget extends StatefulWidget {
  final Widget child;
  final String shareText;
  const ShareableMatchWidget({super.key, required this.child, required this.shareText});

  @override
  State<ShareableMatchWidget> createState() => ShareableMatchWidgetState();
}

class ShareableMatchWidgetState extends State<ShareableMatchWidget> {
  final GlobalKey _boundaryKey = GlobalKey();

  Future<void> captureAndShare() async {
    try {
      final RenderRepaintBoundary? boundary = _boundaryKey.currentContext?.findRenderObject() as RenderRepaintBoundary?;
      if (boundary == null) return;
      final ui.Image image = await boundary.toImage(pixelRatio: 3.0);
      final ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      if (byteData != null) {
        final Uint8List pngBytes = byteData.buffer.asUint8List();
        final Directory tempDir = await getTemporaryDirectory();
        final File imgFile = File('${tempDir.path}/match_${DateTime.now().millisecondsSinceEpoch}.png');
        await imgFile.writeAsBytes(pngBytes);
        await Share.shareXFiles([XFile(imgFile.path)], text: widget.shareText);
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(
      key: _boundaryKey,
      child: Container(
        color: const Color(0xFF0F172A),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            widget.child,
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 14),
              color: const Color(0xFF1E293B),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('تطبيق الكرة المصرية 🇪🇬⚽', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
                  Text('تابع فريقك لحظة بلحظة 📲', style: TextStyle(fontSize: 10, color: Color(0xFF38BDF8))),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
