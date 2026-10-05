import 'package:flutter_test/flutter_test.dart';

import 'package:dashboard_app/main.dart';

void main() {
  testWidgets('Dashboard se renderiza', (WidgetTester tester) async {
    await tester.pumpWidget(const DashboardApp());
    expect(find.text('Panel de control'), findsOneWidget);
  });
}
