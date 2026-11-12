# Next Chapter

A Flutter web demo for exploring master's universities and asking school-specific questions.

## Run

```sh
flutter pub get
flutter run -d chrome
```

## Demo flow

Search universities or filter by field, select a school, then ask the study guide about study options, location, or an application checklist. Questions outside the sample knowledge trigger an alumni-question placeholder. No email is sent or persisted. On narrow screens the chat sits below the profile.

All profiles are illustrative. This demo uses local data and deterministic replies, with no chatbot dependency, AI API, database, authentication, or email service.

## Next implementation step

Keep the Flutter UI independent of a backend. A backend should retrieve verified school information with sources, answer only from that evidence, and offer a reviewed alumni question when the answer is missing. Alumni should opt in; email credentials and AI keys must stay on the server. Alumni responses should be reviewed and permissioned before becoming searchable knowledge. A chat UI library can replace the message presentation later without owning these workflows.

## Validate

```sh
flutter analyze
flutter test
flutter build web
```

## Deploy on Vercel

Import this GitHub repository into Vercel and select **Other** as the framework preset. Keep the repository root as the root directory. The committed `vercel.json` runs `scripts/vercel-build.sh` and serves `build/web`. The script installs the exact Flutter SDK revision used locally, resolves dependencies, and builds the release app. The first cloud build downloads the SDK and requires outbound network access. No environment variables are needed for this demo.

Vercel deployment itself has not been verified by the local checks.
