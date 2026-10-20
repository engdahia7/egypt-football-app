import 'package:flutter/material.dart';
import '../core/app_constants.dart';
import '../core/smart_api_cache.dart';
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
  List<dynamic> matches = [];
  FavoriteTeam? favoriteTeam;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _initData();
  }

  Future<void> _initData() async {
    favoriteTeam = await FavoriteTeamManager.getFavorite();
    await loadMatches();
  }

  String format365Date(DateTime d) =>
      "${d.day.toString().padLeft(2, '0')}/${d.month.toString().padLeft(2, '0')}/${d.year}";

  String formatDisplayDate(DateTime d) =>
      "${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}";

  Future<void> loadMatches({bool forceRefresh = false}) async {
    setState(() {
      isLoading = true;
      errorMessage = null;
    });

    final String dateParam = format365Date(selectedDate);
    final String url =
        'https://appws.365scores.com/web/games/allscores/?langId=27&timezoneName=Africa/Cairo&userCountryId=131&startDate=$dateParam&endDate=$dateParam&competitions=${AppConstants.egyptCompetitions}';

    try {
      final data = await SmartApiCache.get(
        cacheKey: 'matches_${formatDisplayDate(selectedDate)}',
        url: url,
        ttl: const Duration(minutes: 2),
        forceRefresh: forceRefresh,
      );

      setState(() {
        matches = data['games'] ?? [];
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        errorMessage = 'خطأ في الاتصال بالسيرفر: $e';
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('مباريات الكرة المصرية 🇪🇬',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF38BDF8)),
            tooltip: 'تحديث فوري',
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
                    setState(() => selectedDate =
                        selectedDate.subtract(const Duration(days: 1)));
                    loadMatches();
                  },
                  icon: const Icon(Icons.arrow_back_ios, size: 18),
                ),
                Text(formatDisplayDate(selectedDate),
                    style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF38BDF8))),
                IconButton(
                  onPressed: () {
                    setState(() => selectedDate =
                        selectedDate.add(const Duration(days: 1)));
                    loadMatches();
                  },
                  icon: const Icon(Icons.arrow_forward_ios, size: 18),
                ),
              ],
            ),
          ),
          FavoriteTeamBanner(
            favoriteTeam: favoriteTeam,
            allMatches: matches,
            onSelectTeamClicked: _openTeamSelector,
          ),
          Expanded(
            child: isLoading
                ? const Center(
                    child: CircularProgressIndicator(color: Color(0xFF38BDF8)))
                : errorMessage != null
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(errorMessage!,
                                  textAlign: TextAlign.center,
                                  style: const TextStyle(
                                      color: Colors.redAccent, fontSize: 13)),
                              const SizedBox(height: 12),
                              ElevatedButton(
                                onPressed: () => loadMatches(forceRefresh: true),
                                child: const Text('إعادة المحاولة'),
                              ),
                            ],
                          ),
                        ),
                      )
                    : matches.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(Icons.event_busy,
                                    size: 48, color: Colors.white38),
                                const SizedBox(height: 10),
                                const Text(
                                  'لا توجد مباريات مسجلة في هذا اليوم 📅',
                                  style: TextStyle(
                                      color: Colors.white54, fontSize: 14),
                                ),
                                const SizedBox(height: 6),
                                const Text(
                                  'استخدم الأسهم العلوية للتنقل بين الأيام',
                                  style: TextStyle(
                                      color: Colors.white38, fontSize: 12),
                                ),
                              ],
                            ),
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.symmetric(horizontal: 12),
                            itemCount: matches.length,
                            itemBuilder: (context, index) =>
                                MatchCard(match: matches[index]),
                          ),
          ),
        ],
      ),
    );
  }
}
