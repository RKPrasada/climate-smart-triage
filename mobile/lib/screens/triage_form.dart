// mobile/lib/screens/triage_form.dart  —  ClimateSmartTriage
// Patient vitals entry form + AI triage trigger.
// Apache 2.0 — see LICENSE

import 'package:easy_localization/easy_localization.dart';
import 'package:flutter/material.dart';

class TriageFormScreen extends StatefulWidget {
  const TriageFormScreen({super.key});
  @override
  State<TriageFormScreen> createState() => _TriageFormScreenState();
}

class _TriageFormScreenState extends State<TriageFormScreen> {
  final _formKey = GlobalKey<FormState>();

  final _ageCtrl   = TextEditingController();
  final _weightCtrl= TextEditingController();
  final _tempCtrl  = TextEditingController();
  final _rrCtrl    = TextEditingController();
  final _hrCtrl    = TextEditingController();
  final _complCtrl = TextEditingController();

  final Map<String, bool> _symptoms = {
    'fever': false, 'cough': false, 'diarrhea': false,
    'vomiting': false, 'lethargy': false, 'poor_feeding': false,
    'rash': false, 'convulsions': false,
  };

  bool _loading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title:           Text('triage.title'.tr()),
        backgroundColor: const Color(0xFF006666),
        foregroundColor: Colors.white,
      ),
      body: _loading
          ? Center(child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const CircularProgressIndicator(),
                const SizedBox(height: 16),
                Text('triage.analysing'.tr()),
              ],
            ))
          : Form(
              key: _formKey,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _field('triage.age_months'.tr(), _ageCtrl, TextInputType.number),
                  _field('triage.weight_kg'.tr(), _weightCtrl, TextInputType.number),
                  _field('triage.temperature'.tr(), _tempCtrl, TextInputType.number),
                  _field('triage.respiratory_rate'.tr(), _rrCtrl, TextInputType.number),
                  _field('triage.heart_rate'.tr(), _hrCtrl, TextInputType.number),
                  _field('triage.chief_complaint'.tr(), _complCtrl, TextInputType.text,
                         maxLines: 2),
                  const SizedBox(height: 16),
                  Text('triage.symptoms'.tr(),
                       style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8, runSpacing: 8,
                    children: _symptoms.keys.map((key) {
                      return FilterChip(
                        label:     Text('symptoms.$key'.tr()),
                        selected:  _symptoms[key]!,
                        onSelected: (v) => setState(() => _symptoms[key] = v),
                        selectedColor: const Color(0xFF006666).withOpacity(0.2),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    icon:  const Icon(Icons.medical_services),
                    label: Text('triage.submit'.tr()),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF006666),
                      foregroundColor: Colors.white,
                      padding:         const EdgeInsets.all(16),
                      textStyle:       const TextStyle(fontSize: 16,
                                                       fontWeight: FontWeight.bold),
                    ),
                    onPressed: _submit,
                  ),
                ],
              ),
            ),
    );
  }

  Widget _field(String label, TextEditingController ctrl,
                TextInputType type, {int maxLines = 1}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextFormField(
        controller: ctrl,
        keyboardType: type,
        maxLines: maxLines,
        decoration: InputDecoration(
          labelText:    label,
          border:       const OutlineInputBorder(),
          filled:       true,
          fillColor:    Colors.grey.shade50,
        ),
        validator: (v) => (v == null || v.isEmpty) ? 'Required' : null,
      ),
    );
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);

    // In production: call AIService.triage(vitals, climate)
    // Here we simulate a 3-second inference delay
    Future.delayed(const Duration(seconds: 3), () {
      if (!mounted) return;
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content:         Text('URGENT — Refer to health facility within 2 hours.'),
          backgroundColor: Colors.orange,
          duration:        Duration(seconds: 5),
        ),
      );
    });
  }
}
