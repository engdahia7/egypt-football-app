import os

WORKFLOW_CONTENT = r'''
name: Build Compact APK (365Scores Engine)

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - uses: subosito/flutter-action@v2
        with:
          channel: 'stable'

      - name: Create Android Platform
        run: flutter create --platforms=android --org com.egyptfootball.app .

      - name: Add Internet Permission & App Name
        run: |
          sed -i 's/<application/<uses-permission android:name="android.permission.INTERNET"\/><application/g' android/app/src/main/AndroidManifest.xml
          sed -i 's/android:label="[^"]*"/android:label="الكرة المصرية"/g' android/app/src/main/AndroidManifest.xml

      - name: Get Dependencies
        run: flutter pub get

      - name: Build Optimized Split APK
        run: flutter build apk --release --split-per-abi

      - name: Upload Compact APK (arm64-v8a)
        uses: actions/upload-artifact@v4
        with:
          name: Egyptian-Football-Compact-APK
          path: build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
'''

def update_workflow():
    workflow_path = ".github/workflows/build_apk.yml"
    folder = os.path.dirname(workflow_path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(workflow_path, "w", encoding="utf-8") as f:
        f.write(WORKFLOW_CONTENT.strip() + "\n")
    print(f"✅ تم تحديث إعدادات البناء السحابي لتقليص الحجم في: {workflow_path}")

if __name__ == "__main__":
    update_workflow()