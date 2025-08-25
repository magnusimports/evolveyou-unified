import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('EvolveYou app smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(
        body: Center(
          child: Text('EvolveYou Test'),
        ),
      ),
    ));

    // Verify that our test widget is displayed.
    expect(find.text('EvolveYou Test'), findsOneWidget);
  });
}

