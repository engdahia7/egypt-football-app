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
  String? errorMsg;
  int totalFromApi = 0;

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
    setState(() {
      isLoading = true;
      errorMsg = null;
    });
    final String dateStr = formatDate(selectedDate);
    try {
      final data = await SmartApiCache.get(
        cacheKey: 'matches_$dateStr',
        url: 'https://v3.football.api-sports.io/fixtures?date=$dateStr&timezone=Africa/Cairo',
        ttl: const Duration(minutes: 15),
        forceRefresh: forceRefresh,
      );

      String? apiError;
      final errors = data['errors'];
      if (errors is Map && errors.isNotEmpty) {
        apiError = errors.values.join(' | ');
      } else if (errors is List && errors.isNotEmpty) {
        apiError = errors.join(' | ');
      }

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
        totalFromApi = allMatches.length;
        errorMsg = apiError;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMsg = e.toString();
        isLoading = false;
      });
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

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              errorMsg != null
                  ? 'حدث خطأ أثناء جلب البيانات:'
                  : 'لا توجد مباريات للفرق المصرية في هذا اليوم',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.white54),
            ),
            if (errorMsg != null) ...[
              const SizedBox(height: 10),
              Text(errorMsg!,
                  textAlign: TextAlign.center,
                  textDirection: TextDirection.ltr,
                  style: const TextStyle(color: Colors.redAccent, fontSize: 12)),
            ] else ...[
              const SizedBox(height: 10),
              Text('عدد المباريات العالمية المستلمة: $totalFromApi',
                  style: const TextStyle(color: Colors.white38, fontSize: 12)),
            ],
          ],
        ),
      ),
    );
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
                    ? _buildEmptyState()
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
