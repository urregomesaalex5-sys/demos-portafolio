import 'package:flutter_test/flutter_test.dart';

import 'package:gastos_personal/main.dart';

void main() {
  testWidgets('App carga correctamente', (WidgetTester tester) async {
    await tester.pumpWidget(const GastosApp());
    expect(find.text('Mis Gastos'), findsOneWidget);
  });
}
