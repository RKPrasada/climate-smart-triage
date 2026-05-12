// mobile/lib/screens/home_screen.dart  —  ClimateSmartTriage
// Apache 2.0 — see LICENSE

import 'package:easy_localization/easy_localization.dart';
import 'package:flutter/material.dart';
import 'triage_form.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title:           Text('app_title'.tr()),
        backgroundColor: const Color(0xFF006666),
        foregroundColor: Colors.white,
        actions: [
          // Language switcher
          PopupMenuButton<String>(
            icon: const Icon(Icons.language),
            onSelected: (lang) => context.setLocale(Locale(lang)),
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'en', child: Text('English')),
              PopupMenuItem(value: 'te', child: Text('Telugu (తెలుగు)')),
              PopupMenuItem(value: 'hi', child: Text('Hindi (हिंदी)')),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // Offline status banner
          Container(
            width:   double.infinity,
            color:   Colors.orange.shade700,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                const Icon(Icons.wifi_off, color: Colors.white, size: 16),
                const SizedBox(width: 8),
                Text('offline.banner'.tr(),
                     style: const TextStyle(color: Colors.white, fontSize: 13)),
                const Spacer(),
                Text('offline.sync_pending'.tr(namedArgs: {'n': '3'}),
                     style: const TextStyle(color: Colors.white70, fontSize: 12)),
              ],
            ),
          ),

          // Climate alert card
          Padding(
            padding: const EdgeInsets.all(16),
            child: Card(
              color: Colors.red.shade50,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    const Icon(Icons.warning_amber_rounded, color: Colors.red, size: 32),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('home.climate_alert_title'.tr(),
                               style: const TextStyle(fontWeight: FontWeight.bold,
                                                      fontSize: 14)),
                          const SizedBox(height: 4),
                          const Text('Monsoon week 5. Malaria risk HIGH. '
                                     'Suspect malaria for any fever.',
                                     style: TextStyle(fontSize: 13)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Quick action grid
          Expanded(
            child: GridView.count(
              crossAxisCount: 2,
              padding:        const EdgeInsets.symmetric(horizontal: 16),
              crossAxisSpacing: 12,
              mainAxisSpacing:  12,
              children: [
                _ActionCard(
                  icon:    Icons.medical_services,
                  label:   'home.new_triage'.tr(),
                  color:   const Color(0xFF006666),
                  onTap:   () => Navigator.push(context,
                               MaterialPageRoute(builder: (_) => const TriageFormScreen())),
                ),
                _ActionCard(
                  icon:  Icons.history,
                  label: 'home.view_history'.tr(),
                  color: Colors.blueGrey.shade700,
                  onTap: () {},
                ),
                _ActionCard(
                  icon:  Icons.cloud,
                  label: 'home.climate_data'.tr(),
                  color: Colors.teal.shade700,
                  onTap: () {},
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String   label;
  final Color    color;
  final VoidCallback onTap;

  const _ActionCard({
    required this.icon, required this.label,
    required this.color, required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        decoration: BoxDecoration(
          color:        color,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: Colors.white, size: 40),
            const SizedBox(height: 8),
            Text(label, style: const TextStyle(color: Colors.white,
                                               fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}
