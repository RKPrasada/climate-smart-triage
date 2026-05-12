// mobile/lib/main.dart  —  ClimateSmartTriage
// Apache 2.0 — see LICENSE

import 'package:easy_localization/easy_localization.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await EasyLocalization.ensureInitialized();
  runApp(
    EasyLocalization(
      supportedLocales: const [Locale('en'), Locale('te'), Locale('hi')],
      path:            'assets/translations',
      fallbackLocale:  const Locale('en'),
      child:           const ClimateSmartTriageApp(),
    ),
  );
}

class ClimateSmartTriageApp extends StatelessWidget {
  const ClimateSmartTriageApp({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      title:                   'app_title'.tr(),
      localizationsDelegates:  context.localizationDelegates,
      supportedLocales:        context.supportedLocales,
      locale:                  context.locale,
      theme: ThemeData(
        colorScheme:     ColorScheme.fromSeed(seedColor: const Color(0xFF006666)),
        useMaterial3:    true,
        fontFamily:      'Noto Sans Telugu',
      ),
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
