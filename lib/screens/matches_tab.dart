import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../core/smart_api_cache.dart';
import '../core/notification_service.dart';
import '../models/favorite_team.dart';
import '../widgets/favorite_team_banner.dart';
import '../widgets/match_card.dart';

class CachedMatchesTab extends StatefulWidget {
  const CachedMatchesTab({super.key});

  @override
  State<CachedMatchesTab> createState() => _CachedMatchesTabState();
}

class _CachedMatchesTabState extends State<CachedMatchesTab> {
  DateTime selectedDate = DateTime.now();
  bool isLoading = false;
  List<dynamic> filteredMatches = [];
  FavoriteTeam? favoriteTeam;

  @override
  void initState() {
    super.initState();
    _initData();
  }

  Future<void> _initData() async {
    favoriteTeam = await FavoriteTeamManager.getFavorite();
    await loadMatches();
  }

  String formatDate(DateTime date) =>
      "${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}";

  Future<void> loadMatches({bool forceRefresh = false}) async {
    setState(() => isLoading = true);
    final String dateStr = formatDate(selectedDate);
    try {
      final data = await SmartApiCache.get(
        cacheKey: 'matches_$dateStr',
        url: 'https://v3.football.api-sports.io/fixtures?date=$dateStr&timezone=Africa/Cairo',
        ttl: const Duration(minutes: 15),
        forceRefresh: forceRefresh,
      );
      final List<dynamic> allMatches = data['response'] ?? [];
      final List<dynamic> egyptMatches = allMatches.where((match) {
        final int leagueId = match['league']['id'];
        final String country = match['league']['country'] ?? '';
        final int homeId = match['teams']['home']['id'];
        final int awayId = match['teams']['away']['id'];
        return country == 'Egypt' ||
            AppConstants.egyptianLeagueIds.contains(leagueId) ||
            AppConstants.egyptianTeamIds.contains(homeId) ||
            AppConstants.egyptianTeamIds.contains(awayId);
      }).toList();

      setState(() {
        filteredMatches = egyptMatches;
        isLoading = false;
      });
    } catch (_) {
      setState(() => isLoading = false);
    }
  }

  void _openTeamSelector() {
    showDialog(
      context: context,
      builder: (_) => SelectFavoriteTeamDialog(
        onTeamSelected: (team) async {
          await FavoriteTeamManager.saveFavorite(team);
          setState(() => favoriteTeam = team);
        },
      ),
    );
  }

  void _toggleNotifications() async {
    if (favoriteTeam != null) {
      setState(() {
        favoriteTeam!.notificationsEnabled = !favoriteTeam!.notificationsEnabled;
      });
      await FavoriteTeamManager.saveFavorite(favoriteTeam!);
      if (!favoriteTeam!.notificationsEnabled) {
        await NotificationService.cancelAllReminders();
      }
    }
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
            onPressed: () => loadMatches(forceRefresh: true),
          ),
        ],
      ),
      body: Column(
        children: [
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
          FavoriteTeamBanner(
            favoriteTeam: favoriteTeam,
            allMatches: filteredMatches,
            onSelectTeamClicked: _openTeamSelector,
            onToggleNotifications: _toggleNotifications,
            translateName: AppConstants.translate,
          ),
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                : filteredMatches.isEmpty
                    ? const Center(child: Text('لا توجد مباريات للفرق المصرية في هذا اليوم', style: TextStyle(color: Colors.white54)))
                    : ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        itemCount: filteredMatches.length,
                        itemBuilder: (context, index) => MatchCard(match: filteredMatches[index]),
                      ),
          ),
        ],
      ),
    );
  }
}
