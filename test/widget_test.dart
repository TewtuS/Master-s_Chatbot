import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:masters_guide/main.dart';

void main() {
  testWidgets(
      'Select a school, query its profile and prepare an alumni question',
      (tester) async {
    tester.view.physicalSize = const Size(1440, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const MastersGuide());
    await tester.tap(find.text('University of Edinburgh'));
    await tester.pumpAndSettle();
    expect(find.text('Your study guide'), findsOneWidget);
    await tester.tap(find.text('Study options'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Source: demo school profile'), findsOneWidget);
    await tester.enterText(
        find.byType(TextField), 'What is student life like?');
    await tester.testTextInput.receiveAction(TextInputAction.done);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Prepare alumni question'));
    await tester.pumpAndSettle();
    expect(find.textContaining('No email was sent or saved.'), findsOneWidget);
    await tester.tap(find.text('All universities'));
    await tester.pumpAndSettle();
    expect(find.text('Explore your possibilities'), findsOneWidget);
  });
  testWidgets('Search handles missing matches', (tester) async {
    await tester.pumpWidget(const MastersGuide());
    await tester.enterText(find.byType(TextField), 'does not exist');
    await tester.pumpAndSettle();
    expect(find.text('No matches. Try another search or field of study.'),
        findsOneWidget);
  });
}
