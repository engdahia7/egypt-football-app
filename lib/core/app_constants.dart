class AppConstants {
  static final Set<int> egyptianLeagueIds = {233, 714, 539, 895};
  static final Set<int> egyptianTeamIds = {
    1023, 1040, 1032, 1029, 1030, 1028, 1036, 1039, 1025, 1037, 1041, 1042, 1026, 1570
  };
  static final Map<String, String> arabicNames = {
    'Al Ahly': 'الأهلي',
    'Zamalek SC': 'الزمالك',
    'Pyramids FC': 'بيراميدز',
    'Al Masry': 'المصري البورسعيدي',
    'Al Ittihad': 'الاتحاد السكندري',
    'Ismaily SC': 'الإسماعيلي',
    'Modern Sport': 'مودرن سبورت',
    'Ceramica Cleopatra': 'سيراميكا كليوباترا',
    'Enppi': 'إنبي',
    'Smouha SC': 'سموحة',
    "Tala'ea El Gaish": 'طلائع الجيش',
    'ZED FC': 'زد إف سي',
    'Ghazl El Mahallah': 'غزل المحلة',
    'Egypt': 'منتخب مصر',
    'Premier League': 'الدوري المصري الممتاز',
    'Egypt Cup': 'كأس مصر',
    'CAF Champions League': 'دوري أبطال أفريقيا',
    'CAF Confederation Cup': 'كأس الكونفدرالية الأفريقية',
    'CAF Super Cup': 'السوبر الأفريقي',
  };
  static String translate(String name) => arabicNames[name] ?? name;
}
