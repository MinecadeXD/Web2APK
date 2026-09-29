<div align="center">

# 🌐 Web2APK

**Turn a website into a lightweight Android APK**

[![Built with HTML](https://img.shields.io/badge/Website-HTTPS-0A66C2?logo=googlechrome&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTTP)
[![Android](https://img.shields.io/badge/Platform-Android-3DDC84?logo=android&logoColor=white)](https://developer.android.com)
[![Python](https://img.shields.io/badge/Build_Script-Python-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Java](https://img.shields.io/badge/Java-17-ED8B00?logo=openjdk&logoColor=white)](https://www.oracle.com/java/)
<br>
[![GitHub Actions](https://img.shields.io/badge/Build-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*A simple, configuration-driven Android wrapper for websites. Configure your website once, let GitHub Actions build the APK, and download the generated artifact.*

</div>

---

## ✨ Features

- 🌐 Wrap any **HTTPS website** in an Android application.
- ⚙️ Configure the app from a single file: `config/app.yml`.
- 🏷️ Custom app name and Android package suffix.
- 🔢 Semantic app versioning with automatic Android `versionCode` generation.
- 🖼️ Custom PNG, JPG, or JPEG launcher icon.
- 🔤 Automatic letter-icon fallback when the configured icon is missing.
- 🎨 Custom splash-screen background color.
- 🎨 Custom Android Custom Tab toolbar color.
- 📝 Option to show or hide the website title in the toolbar.
- 📱 Optional URL-bar hiding while scrolling.
- 🔒 HTTPS-only URL validation.
- 🧹 Generated Android resources are cleaned before every build.
- 🛡️ Release builds use R8/minification and resource shrinking.
- ✅ CI verifies the generated APK's signature and important Android metadata.
- 📋 GitHub Actions generates a build summary containing the app name, package, version, website URL, and APK filename.
- 📦 Generated APKs are uploaded as GitHub Actions artifacts.
- 🚫 Automatic builds run only when `config/app.yml` changes on `main`.
- ▶️ Builds can also be started manually with **workflow_dispatch**.

---

## 📖 How Web2APK Works

Web2APK keeps the Android project small and puts the customization in `config/app.yml`.

The build process is:

```text
config/app.yml
      │
      ▼
scripts/prepare_build.py
      │
      ├── Validate configuration
      ├── Check version/tag rules
      ├── Clean generated resources
      ├── Generate icon and Android resources
      └── Export build values to GitHub Actions
      │
      ▼
GitHub Actions
      │
      ├── Set up Python
      ├── Set up Java 17
      ├── Build release APK with Gradle
      ├── Verify APK
      ├── Generate build summary
      └── Upload APK artifact
      │
      ▼
Generated Android APK
```

The Android application opens the configured website using an Android **Custom Tab**. If a Custom Tab is unavailable, the application can fall back to the available browser handling on the device.

---

## 🚀 Quick Start

### 1. Fork the repository

Fork this repository to your own GitHub account.

You do not need to copy any private credentials from the original repository. GitHub Actions secrets are not transferred to forks.

### 2. Edit the configuration

Open:

```text
config/app.yml
```

Change the values to match your website and app.

For example:

```yaml
app_name: "My Website"
website_url: "https://example.com/"
version: "1.0.0"
package_suffix: "mywebsite"

icon: "config/icon.png"

splash_background: "#FFFFFF"
toolbar_color: "#121212"

show_title: true
url_bar_hiding: true
```

### 3. Add your icon (optional)

If you want a custom launcher icon, place a PNG, JPG, or JPEG file inside the repository and point `icon` to it.

Recommended:

- Square image
- 1024 × 1024 px
- At least 192 × 192 px
- PNG, JPG, or JPEG
- RGB or RGBA

If the configured file does not exist, Web2APK automatically generates a simple icon using the first letter of the app name.

### 4. Commit the configuration

Commit and push your changes to the `main` branch.

Because the workflow is path-filtered, a push to `main` automatically starts a build **only when `config/app.yml` changed**.

### 5. Get the APK

After the workflow finishes successfully:

1. Open the repository's **Actions** tab.
2. Open the completed **Build Web2APK** workflow run.
3. Check the generated **Web2APK Build Summary**.
4. Download the APK from the workflow's **Artifacts** section.
5. Install the APK on your Android device.

You can also start a build manually from **Actions → Build Web2APK → Run workflow**.

---

## ⚙️ Configuration

All user-facing build settings are stored in:

```text
config/app.yml
```

### `app_name`

The name displayed by Android for the generated application.

```yaml
app_name: "My Website"
```

**Allowed:** 1–60 characters.

---

### `website_url`

The website opened when the app starts.

```yaml
website_url: "https://example.com/"
```

**Allowed:** a complete HTTPS URL.

HTTP URLs are rejected by the build validation.

---

### `version`

The Android application version in `MAJOR.MINOR.PATCH` format.

```yaml
version: "1.2.3"
```

Minor and patch values must be between `0` and `999`.

Web2APK automatically converts the version into an Android `versionCode`:

```text
MAJOR × 1,000,000
+ MINOR × 1,000
+ PATCH
```

For example:

```text
1.2.3 → 1,002,003
```

The build also checks Git tags so an already-used version cannot accidentally be reused.

---

### `package_suffix`

The final part of the Android package name.

```yaml
package_suffix: "mywebsite"
```

This produces:

```text
com.minecade.mywebsite
```

**Allowed:**

- Lowercase letters
- Numbers
- Periods
- Multiple package segments

Each segment must start and end with a letter or number.

Examples:

```yaml
package_suffix: "website"
package_suffix: "mywebsite"
package_suffix: "projects.website"
```

The reserved debug package form is rejected.

> **Fork note:** The package namespace currently uses the `com.minecade.*` prefix. If you plan to distribute your fork as your own independent Android project, review the Android package/namespace configuration before publishing.

---

### `icon`

Path to the launcher icon.

```yaml
icon: "config/icon.png"
```

Supported formats:

- PNG
- JPG
- JPEG

The source image must be at least 192 × 192 px.

If the file is missing, Web2APK generates an automatic letter icon.

---

### `splash_background`

Background color used by the splash screen and generated adaptive icon background.

```yaml
splash_background: "#121212"
```

Allowed values:

```yaml
splash_background: white
splash_background: black
splash_background: "#121212"
```

Only `white`, `black`, or a 6-digit hexadecimal color is accepted.

---

### `toolbar_color`

Color used by the Android Custom Tab toolbar.

```yaml
toolbar_color: "#121212"
```

Allowed values are `white`, `black`, or a 6-digit hexadecimal color.

---

### `show_title`

Controls whether the website title is shown in the Custom Tab toolbar.

```yaml
show_title: true
```

Allowed values:

```yaml
show_title: true
show_title: false
```

---

### `url_bar_hiding`

Controls whether the Custom Tab URL bar can hide while the website is scrolled.

```yaml
url_bar_hiding: true
```

Allowed values:

```yaml
url_bar_hiding: true
url_bar_hiding: false
```

---

## 🧪 Validation

Web2APK validates the configuration before starting the Android build.

The build fails when, for example:

- `config/app.yml` is missing.
- YAML is invalid.
- A required value is empty.
- The app name is outside the allowed length.
- The website URL is not HTTPS.
- The version is not valid `MAJOR.MINOR.PATCH`.
- The generated Android `versionCode` is invalid or outside the supported range.
- The version already exists as a Git tag.
- The package suffix contains invalid characters.
- The package suffix is too long.
- The package suffix produces a reserved debug package name.
- A color value is invalid.
- A supplied icon uses an unsupported format.
- A supplied icon is too small.

This prevents invalid configuration from reaching the Android build stage.

---

## 🔢 Versioning

Web2APK uses two related Android version values:

| Value | Source |
|---|---|
| Version name | `version` in `config/app.yml` |
| Version code | Automatically generated from `version` |

For example:

| Version | Android versionCode |
|---|---:|
| `1.0.0` | `1000000` |
| `1.2.3` | `1002003` |
| `2.0.0` | `2000000` |

Avoid reusing a version that already has a corresponding Git tag.

---

## 🔐 APK Signing

The repository's current build configuration creates a technically signed release APK using the Android/Gradle debug signing configuration.

This is useful for simple testing and GitHub Actions builds, but **it is not the same as signing an app with your own production release keystore**.

If you fork Web2APK and intend to publish your APK through an app store or maintain long-term public releases:

1. Create your own Android release keystore.
2. Store signing credentials securely as GitHub Actions secrets.
3. Configure your fork's release build to use those credentials.
4. Never commit a keystore or signing passwords to the repository.
5. Keep the same signing key for future updates of the same published Android application.

GitHub Actions secrets from the original repository are not copied into forks.

---

## 🤖 GitHub Actions

The workflow is located at:

```text
.github/workflows/build.yml
```

### Automatic builds

A build automatically starts when:

- the branch is `main`
- and `config/app.yml` changed

Changes to unrelated files do not automatically trigger the workflow.

### Manual builds

The workflow also supports manual execution through GitHub Actions:

```text
Actions
→ Build Web2APK
→ Run workflow
```

### Build stages

The workflow:

1. Checks out the repository.
2. Sets up Python 3.12.
3. Installs the build-script dependencies.
4. Validates the configuration.
5. Generates Android resources.
6. Sets up Java 17.
7. Sets up Gradle.
8. Builds the release APK.
9. Renames the APK.
10. Verifies the APK signature and metadata.
11. Generates a GitHub Actions summary.
12. Uploads the APK as an artifact.

---

## 🛡️ Release Build Checks

The CI workflow verifies that the generated APK:

- Exists at the expected path.
- Has a valid Android APK signature.
- Contains the expected package name.
- Contains the expected version name.
- Contains the expected version code.
- Contains the expected application name.

The release build also enables:

- **R8 / code minification**
- **Resource shrinking**

This keeps the generated APK smaller and removes unused code/resources where possible.

---

## 📦 APK Output

The generated APK is renamed using this format:

```text
<AppName>-v<Version>.apk
```

Example:

```text
My Website-v1.0.0.apk
```

The APK is uploaded to the GitHub Actions workflow run as an artifact.

---

## 🗂️ Repository Structure

```text
Web2APK/
├── .github/
│   └── workflows/
│       └── build.yml
├── app/
│   ├── build.gradle.kts
│   └── src/
│       └── main/
│           └── res/
├── config/
│   └── app.yml
├── scripts/
│   └── prepare_build.py
├── .gitignore
├── LICENSE
├── README.md
├── build.gradle.kts
├── gradle.properties
└── settings.gradle.kts
```

Generated files are intentionally ignored where appropriate and recreated during the build.

---

## 🧹 Clean Builds

Before generating Android resources, Web2APK removes previously generated resources such as:

- Generated launcher icons
- Generated splash icon
- Generated color resources
- Generated configuration resources
- Generated adaptive icon resources

This prevents stale configuration from leaking into a later build.

---

## 💻 Local Development

The normal intended workflow is **GitHub Actions**, so you do not need Android Studio just to generate the APK.

For development or troubleshooting, the repository contains a standard Gradle Android project.

The build environment used by CI includes:

- Python 3.12
- Java 17
- Gradle 9.6.0
- Android SDK / Android Gradle Plugin
- Python packages: PyYAML and Pillow

The configuration script expects to run inside GitHub Actions because it writes build values to the GitHub Actions environment.

---

## 📱 Android Compatibility

The application is configured with:

- **Minimum Android SDK:** 23
- **Target Android SDK:** 36
- **Compile SDK:** 36

The final website experience can still depend on the Android device's browser/Custom Tab implementation and the website itself.

---

## 🌐 Website Requirements

Your website should:

- Use HTTPS.
- Be accessible from the Android device.
- Work correctly in a mobile browser.
- Have responsive/mobile-friendly layouts if you want a good phone experience.
- Not rely on desktop-only interactions.
- Allow required JavaScript, cookies, storage, authentication, and other browser functionality as needed by the site.

Web2APK does not convert a website into native Android screens. It packages a lightweight Android application that opens the website through Android's browser-based Custom Tab experience.

---

## ⚠️ Important Limitations

Web2APK is a **website wrapper**, not a website-to-native-code converter.

That means:

- Your website still needs to be online.
- The app needs network access to load the website.
- Offline functionality is determined by the website, not Web2APK.
- Website compatibility depends on Android browser support.
- Web2APK does not automatically add native Android features to the website.
- Native APIs that require a dedicated Android implementation are not automatically available.
- Authentication, downloads, file uploads, payments, pop-ups, and other browser features can behave differently depending on the website and device.

---

## 🐛 Troubleshooting

### The workflow does not start

Check that:

- Your changes were pushed to `main`.
- `config/app.yml` was included in the commit.
- The workflow is enabled.
- You did not expect a build from a change to another file; automatic builds are intentionally limited to `config/app.yml` changes.

You can use **Run workflow** for a manual build.

### Configuration validation fails

Open the failed workflow and inspect the **Validate configuration and generate Android resources** step.

The error message identifies the configuration value that needs to be corrected.

### The icon is not used

Check:

- The path in `icon` is correct.
- The file exists in the repository.
- The file is PNG, JPG, or JPEG.
- The image is at least 192 × 192 px.

If the file is missing, the automatic letter icon is used instead.

### The website does not load

Check:

- The URL starts with `https://`.
- The website is publicly reachable.
- The device has an internet connection.
- The website works in the device's normal browser.
- The website does not block the browser environment used by the Custom Tab.

### The APK verification step fails

Check the workflow output for the specific failed check. The verification stage compares the APK against the values generated from `config/app.yml`.

---

## 🔒 Security Notes

- Do not put passwords, API keys, tokens, or private credentials in `config/app.yml`.
- Do not commit Android keystores.
- Do not commit signing passwords.
- Use GitHub Actions secrets for sensitive CI credentials.
- Review third-party website content and permissions before distributing a generated APK.
- Remember that the generated APK is a wrapper around the configured website; the website itself remains responsible for its own security.

---

## 🤝 Contributing

Contributions are welcome.

Before making a pull request:

1. Keep the project focused on website-to-APK generation.
2. Avoid committing generated build output.
3. Keep configuration validation strict and predictable.
4. Update documentation when user-facing behavior changes.
5. Test the GitHub Actions build when changing build or workflow logic.
6. Avoid introducing personal or environment-specific data.

---

## 📄 License

Web2APK is released under the **MIT License**.

See [LICENSE](LICENSE) for the full license text.

---

## 👤 Author

Developed by **Minecade**.

---

## ⭐ Support the Project

If Web2APK is useful to you:

- ⭐ Star the repository.
- 🐛 Report reproducible bugs through GitHub Issues.
- 💡 Suggest improvements through GitHub Issues.
- 🔧 Submit pull requests for useful, tested improvements.

---

<div align="center">

**Web2APK — configure once, build with GitHub Actions, get an Android APK.**

</div>
