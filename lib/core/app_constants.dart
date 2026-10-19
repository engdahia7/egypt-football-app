class AppConstants {
  // أكواد البطولات في 365Scores:
  // 552: الدوري المصري | 553: كأس مصر | 1129: السوبر المصري
  // 572: دوري أبطال أفريقيا | 573: الكونفدرالية الأفريقية
  static const String egyptCompetitions = '552,553,1129,572,573';

  static String teamLogo(int teamId) =>
      'https://imagecache.365scores.com/image/upload/f_png,w_80,h_80,c_limit,q_auto:eco,d_Competitors:default1.png/v1/Competitors/$teamId';

  static String competitionLogo(int compId) =>
      'https://imagecache.365scores.com/image/upload/f_png,w_64,h_64,c_limit,q_auto:eco,d_Countries:Round:default.png/v1/Competitions/$compId';

  static String playerPhoto(int athleteId) =>
      'https://imagecache.365scores.com/image/upload/f_png,w_80,h_80,c_limit,q_auto:eco,d_Athletes:default.png/v1/Athletes/$athleteId';
}
