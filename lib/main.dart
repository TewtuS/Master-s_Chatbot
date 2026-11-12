import 'package:flutter/material.dart';

void main() => runApp(const MastersGuide());

const ink = Color(0xFF192F2B);
const green = Color(0xFF246B54);
const cream = Color(0xFFF6F5F0);

class School {
  final String name, city, country, initials, description;
  final List<String> subjects;
  final Color color;
  const School(this.name, this.city, this.country, this.initials,
      this.description, this.subjects, this.color);
}

const schools = [
  School(
      'University of Edinburgh',
      'Edinburgh',
      'United Kingdom',
      'E',
      'A historic university in a city full of ideas. Explore a research-led learning environment and a vibrant international student community.',
      ['Computer Science', 'Business', 'Engineering'],
      Color(0xFFDCE5DD)),
  School(
      'Delft University of Technology',
      'Delft',
      'Netherlands',
      'D',
      'A technical university with a focus on design, engineering, and solving real-world challenges through collaborative research.',
      ['Engineering', 'Computer Science', 'Design'],
      Color(0xFFDCE8EE)),
  School(
      'University of Melbourne',
      'Melbourne',
      'Australia',
      'M',
      'An urban campus and a broad graduate learning environment, bringing together students across research and professional disciplines.',
      ['Business', 'Engineering', 'Design'],
      Color(0xFFE9E0D3)),
  School(
      'University of British Columbia',
      'Vancouver',
      'Canada',
      'U',
      'A research-focused university surrounded by the Pacific coast, with a diverse community and interdisciplinary graduate study.',
      ['Computer Science', 'Business', 'Engineering'],
      Color(0xFFE0E4D5)),
];

class MastersGuide extends StatelessWidget {
  const MastersGuide({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Next Chapter · Master’s explorer',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
            useMaterial3: true,
            scaffoldBackgroundColor: cream,
            colorScheme: ColorScheme.fromSeed(seedColor: green),
            fontFamily: 'Arial',
            textTheme: const TextTheme(bodyMedium: TextStyle(color: ink))),
        home: const Explorer(),
      );
}

class Explorer extends StatefulWidget {
  const Explorer({super.key});
  @override
  State<Explorer> createState() => _ExplorerState();
}

class _ExplorerState extends State<Explorer> {
  School? selected;
  String query = '', subject = 'All fields';
  final search = TextEditingController();
  @override
  void dispose() {
    search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        body: Column(children: [
          Container(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 21),
              decoration: const BoxDecoration(
                  color: Colors.white,
                  border: Border(bottom: BorderSide(color: Color(0xFFE2E5DE)))),
              child: Row(children: [
                const Icon(Icons.auto_awesome, color: green, size: 27),
                const SizedBox(width: 10),
                const Text('next chapter',
                    style: TextStyle(
                        fontSize: 23,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -1)),
                const Spacer(),
                if (MediaQuery.sizeOf(context).width > 1000)
                  const Text('Your master’s journey starts here',
                      style: TextStyle(color: Colors.black54)),
                const SizedBox(width: 20),
                const Chip(
                    label: Text('DEMO'),
                    side: BorderSide.none,
                    backgroundColor: cream),
              ])),
          Expanded(child: selected == null ? home() : profile(selected!)),
        ]),
      );
  Widget home() {
    final results = schools
        .where((s) =>
            '${s.name} ${s.city} ${s.country}'
                .toLowerCase()
                .contains(query.toLowerCase()) &&
            (subject == 'All fields' || s.subjects.contains(subject)))
        .toList();
    return SingleChildScrollView(
        padding: const EdgeInsets.all(32),
        child: Center(
            child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 1200),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 30),
                      const Text('A BIG NEXT STEP. A LITTLE MORE CLARITY.',
                          style: TextStyle(
                              color: green,
                              fontSize: 12,
                              letterSpacing: 2,
                              fontWeight: FontWeight.bold)),
                      const SizedBox(height: 18),
                      const Text('Find your place.\nShape your next chapter.',
                          style: TextStyle(
                              fontSize: 49,
                              height: 1.12,
                              fontWeight: FontWeight.w700,
                              letterSpacing: -2,
                              color: ink)),
                      const SizedBox(height: 18),
                      const Text(
                          'Explore universities, ask the questions that matter, and learn from\npeople who have already been where you’re going.',
                          style: TextStyle(
                              fontSize: 17,
                              height: 1.6,
                              color: Colors.black54)),
                      const SizedBox(height: 30),
                      TextField(
                          controller: search,
                          onChanged: (v) => setState(() => query = v),
                          decoration: InputDecoration(
                              hintText: 'Search a university, city, or country',
                              prefixIcon: const Icon(Icons.search),
                              filled: true,
                              fillColor: Colors.white,
                              border: OutlineInputBorder(
                                  borderRadius: BorderRadius.circular(14),
                                  borderSide: BorderSide.none))),
                      const SizedBox(height: 18),
                      Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            'All fields',
                            'Computer Science',
                            'Business',
                            'Engineering',
                            'Design'
                          ]
                              .map((v) => ChoiceChip(
                                  label: Text(v),
                                  selected: subject == v,
                                  onSelected: (_) =>
                                      setState(() => subject = v),
                                  selectedColor: const Color(0xFFDCE9DF)))
                              .toList()),
                      const SizedBox(height: 38),
                      Row(children: [
                        const Expanded(
                            child: Text('Explore your possibilities',
                                style: TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold))),
                        Text('${results.length} universities',
                            style: const TextStyle(color: Colors.black54))
                      ]),
                      const SizedBox(height: 8),
                      const Text(
                          'A small selection to get your search started. All content is illustrative.',
                          style: TextStyle(color: Colors.black54)),
                      const SizedBox(height: 22),
                      LayoutBuilder(builder: (context, c) {
                        final width = c.maxWidth > 850
                            ? (c.maxWidth - 48) / 3
                            : c.maxWidth > 560
                                ? (c.maxWidth - 24) / 2
                                : c.maxWidth;
                        return Wrap(
                            spacing: 24,
                            runSpacing: 24,
                            children: results
                                .map((s) => SizedBox(
                                    width: width, child: schoolCard(s)))
                                .toList());
                      }),
                      if (results.isEmpty)
                        const Padding(
                            padding: EdgeInsets.all(36),
                            child: Text(
                                'No matches. Try another search or field of study.')),
                      const SizedBox(height: 35),
                      const Text(
                          'Built around your questions. Informed by shared experience.',
                          style: TextStyle(color: Colors.black45)),
                    ]))));
  }

  Widget schoolCard(School s) => Card(
      clipBehavior: Clip.antiAlias,
      elevation: 0,
      color: Colors.white,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
          side: const BorderSide(color: Color(0xFFE2E5DE))),
      child: InkWell(
          onTap: () => setState(() => selected = s),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Container(
                height: 145,
                color: s.color,
                child: Stack(children: [
                  Positioned(
                      right: -15,
                      bottom: -45,
                      child: Icon(Icons.account_balance,
                          size: 200, color: ink.withValues(alpha: .08))),
                  Center(
                      child: Text(s.initials,
                          style: TextStyle(
                              fontFamily: 'Georgia',
                              fontSize: 78,
                              color: ink.withValues(alpha: .75))))
                ])),
            Padding(
                padding: const EdgeInsets.all(22),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('${s.city}, ${s.country}',
                          style: const TextStyle(
                              fontSize: 12, color: Colors.black54)),
                      const SizedBox(height: 10),
                      SizedBox(
                          height: 55,
                          child: Text(s.name,
                              style: const TextStyle(
                                  fontSize: 21,
                                  fontWeight: FontWeight.bold,
                                  height: 1.25))),
                      const SizedBox(height: 15),
                      Text(s.subjects.take(2).join(' · '),
                          style: const TextStyle(
                              fontSize: 12, color: Colors.black54)),
                      const SizedBox(height: 24),
                      const Row(children: [
                        Text('Explore university',
                            style: TextStyle(
                                color: green, fontWeight: FontWeight.bold)),
                        Spacer(),
                        Icon(Icons.arrow_forward, color: green, size: 19)
                      ])
                    ])),
          ])));
  Widget profile(School s) => LayoutBuilder(builder: (context, c) {
        final details = SingleChildScrollView(
            padding: const EdgeInsets.all(30),
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              TextButton.icon(
                  onPressed: () => setState(() => selected = null),
                  icon: const Icon(Icons.arrow_back, size: 17),
                  label: const Text('All universities')),
              const SizedBox(height: 20),
              Container(
                  height: 170,
                  width: double.infinity,
                  decoration: BoxDecoration(
                      color: s.color, borderRadius: BorderRadius.circular(20)),
                  child: const Icon(Icons.account_balance_outlined,
                      size: 100, color: green)),
              const SizedBox(height: 27),
              Text('${s.city.toUpperCase()}  /  ${s.country.toUpperCase()}',
                  style: const TextStyle(
                      color: green, fontSize: 12, letterSpacing: 1.5)),
              const SizedBox(height: 12),
              Text(s.name,
                  style: const TextStyle(
                      fontSize: 34,
                      fontWeight: FontWeight.bold,
                      letterSpacing: -1)),
              const SizedBox(height: 18),
              Text(s.description,
                  style: const TextStyle(
                      fontSize: 16, height: 1.7, color: Colors.black54)),
              const SizedBox(height: 28),
              const Text('Fields to explore',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 14),
              Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: s.subjects
                      .map((v) => Chip(
                          label: Text(v),
                          backgroundColor: Colors.white,
                          side: BorderSide.none))
                      .toList()),
              const SizedBox(height: 28),
              const Text('Make an informed next step',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              const Text(
                  'Ask about study options, the application process, or student life. For personal experiences, your guide can prepare a question for an alumnus.',
                  style: TextStyle(height: 1.7, color: Colors.black54)),
              const SizedBox(height: 24),
              const ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Icon(Icons.info_outline, color: green),
                  title: Text('Illustrative school profiles'),
                  subtitle: Text(
                      'Program availability, fees, deadlines, and admission requirements must be verified with the university.')),
            ]));
        final chat = ChatPanel(key: ValueKey(s.name), school: s);
        if (c.maxWidth < 800) {
          return ListView(
              children: [details, SizedBox(height: 600, child: chat)]);
        }
        return Row(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Expanded(child: details),
          SizedBox(width: c.maxWidth > 1150 ? 440 : 360, child: chat)
        ]);
      });
}

class ChatPanel extends StatefulWidget {
  final School school;
  const ChatPanel({super.key, required this.school});
  @override
  State<ChatPanel> createState() => _ChatPanelState();
}

class _ChatPanelState extends State<ChatPanel> {
  final input = TextEditingController();
  final scroll = ScrollController();
  final List<({String text, bool user})> messages = [];
  bool alumni = false, prepared = false;
  @override
  void initState() {
    super.initState();
    messages.add((
      text:
          'Hi! I’m your study guide. Let’s explore ${widget.school.name}. What would you like to know?',
      user: false
    ));
  }

  @override
  void dispose() {
    input.dispose();
    scroll.dispose();
    super.dispose();
  }

  void send([String? suggestion]) {
    final question = (suggestion ?? input.text).trim();
    if (question.isEmpty) return;
    final q = question.toLowerCase();
    String answer;
    bool fallback = false;
    if (q.contains('field') ||
        q.contains('program') ||
        q.contains('study options')) {
      answer =
          'The sample profile highlights ${widget.school.subjects.join(', ')}. These are broad fields, not a verified program list. Check the university’s official course directory before applying.\n\nSource: demo school profile';
    } else if (q.contains('where') || q.contains('located')) {
      answer =
          '${widget.school.name} is in ${widget.school.city}, ${widget.school.country}.\n\nSource: demo school profile';
    } else if (q.contains('application') || q.contains('apply')) {
      answer =
          'A useful starting checklist is your bachelor’s transcript, a statement of purpose, references, and any required language test. Exact requirements vary by program. This demo does not hold verified admissions requirements.\n\nSource: general demo guidance';
    } else {
      answer =
          'I don’t have a verified answer to that in the demo knowledge base. You can prepare this question for an alumnus to get a personal perspective. For official requirements, confirm directly with the university.';
      fallback = true;
    }
    setState(() {
      messages.add((text: question, user: true));
      messages.add((text: answer, user: false));
      alumni = fallback;
      prepared = false;
      input.clear();
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (scroll.hasClients) {
        scroll.animateTo(scroll.position.maxScrollExtent,
            duration: const Duration(milliseconds: 250), curve: Curves.easeOut);
      }
    });
  }

  @override
  Widget build(BuildContext context) => Container(
      decoration: const BoxDecoration(
          color: Colors.white,
          border: Border(left: BorderSide(color: Color(0xFFE2E5DE)))),
      child: Column(children: [
        const Padding(
            padding: EdgeInsets.all(24),
            child: Row(children: [
              CircleAvatar(
                  backgroundColor: Color(0xFFE1EDE5),
                  child: Icon(Icons.auto_awesome, color: green)),
              SizedBox(width: 12),
              Expanded(
                  child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                    Text('Your study guide',
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold)),
                    Text('Sample knowledge · Alumni guidance',
                        style: TextStyle(fontSize: 11, color: Colors.black54))
                  ]))
            ])),
        const Divider(height: 1),
        Expanded(
            child: ListView(
                controller: scroll,
                padding: const EdgeInsets.all(20),
                children: messages
                    .map((m) => Align(
                        alignment: m.user
                            ? Alignment.centerRight
                            : Alignment.centerLeft,
                        child: Container(
                            margin: const EdgeInsets.only(bottom: 16),
                            padding: const EdgeInsets.all(17),
                            decoration: BoxDecoration(
                                color: m.user ? green : cream,
                                borderRadius: BorderRadius.circular(16)),
                            child: Text(m.text,
                                style: TextStyle(
                                    color: m.user ? Colors.white : ink,
                                    height: 1.55,
                                    fontSize: 14)))))
                    .toList())),
        if (messages.length == 1)
          Padding(
              padding: const EdgeInsets.symmetric(horizontal: 18),
              child: Wrap(
                  spacing: 6,
                  children: [
                    'Study options',
                    'Application checklist',
                    'Student life'
                  ]
                      .map((q) => ActionChip(
                          label: Text(q, style: const TextStyle(fontSize: 11)),
                          onPressed: () => send(q)))
                      .toList())),
        if (alumni)
          Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              child: Column(children: [
                OutlinedButton.icon(
                    onPressed:
                        prepared ? null : () => setState(() => prepared = true),
                    icon: Icon(prepared ? Icons.check : Icons.mail_outline),
                    label: Text(prepared
                        ? 'Question prepared'
                        : 'Prepare alumni question')),
                if (prepared)
                  const Text(
                      'Demo only: your question is ready for review. No email was sent or saved.',
                      style: TextStyle(fontSize: 12, color: Colors.black54))
              ])),
        Padding(
            padding: const EdgeInsets.fromLTRB(18, 16, 18, 10),
            child: TextField(
                controller: input,
                onSubmitted: (_) => send(),
                decoration: InputDecoration(
                    hintText: 'Ask about this university…',
                    filled: true,
                    fillColor: cream,
                    border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(14),
                        borderSide: BorderSide.none),
                    suffixIcon: IconButton(
                        onPressed: send,
                        icon: const Icon(Icons.arrow_upward, color: green))))),
        const Padding(
            padding: EdgeInsets.only(bottom: 16),
            child: Text('Demo replies · No AI service or email connected',
                style: TextStyle(fontSize: 10, color: Colors.black45))),
      ]));
}
