import 'package:flutter/material.dart';
import 'core/notification_service.dart';
import 'screens/matches_tab.dart';
import 'screens/standings_tab.dart';
import 'screens/scorers_tab.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await NotificationService.init();
  runApp(const EgyptianFootballApp());
}

class EgyptianFootballApp extends StatelessWidget {
  const EgyptianFootballApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'الكرة المصرية',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        cardColor: const Color(0xFF1E293B),
      ),
      home: const Directionality(
        textDirection: TextDirection.rtl,
        child: MainLayoutScreen(),
      ),
    );
  }
}

class MainLayoutScreen extends StatefulWidget {
  const MainLayoutScreen({super.key});

  @override
  State<MainLayoutScreen> createState() => _MainLayoutScreenState();
}

class _MainLayoutScreenState extends State<MainLayoutScreen> {
  int _currentIndex = 0;
  final List<Widget> _screens = const [
    CachedMatchesTab(),
    CachedStandingsTab(),
    CachedScorersTab(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        backgroundColor: const Color(0xFF1E293B),
        selectedItemColor: const Color(0xFF38BDF8),
        unselectedItemColor: Colors.white54,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.sports_soccer), label: 'المباريات'),
          BottomNavigationBarItem(icon: Icon(Icons.leaderboard), label: 'الترتيب'),
          BottomNavigationBarItem(icon: Icon(Icons.emoji_events), label: 'الهدافون'),
        ],
      ),
    );
  }
}
