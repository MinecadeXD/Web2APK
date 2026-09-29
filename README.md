# Web2APK

A lightweight GitHub-based website-to-Android APK converter using Android Custom Tabs.

> 🚧 Project under development.


## Configuration

Edit `config/app.yml` to configure the generated APK. The existing configuration values remain unchanged; appearance options are also available in the same file.

### Appearance options

| Setting | Accepted values | Purpose |
| --- | --- | --- |
| `splash_background` | `white`, `black`, or `#RRGGBB` | Splash screen background |
| `toolbar_color` | `white`, `black`, or `#RRGGBB` | Custom Tab toolbar color |
| `show_title` | `true` / `false` | Show the website title in the Custom Tab |
| `url_bar_hiding` | `true` / `false` | Allow the Custom Tab URL bar to hide while scrolling |

If an appearance option is omitted, Web2APK uses these defaults:

- `splash_background: white`
- `toolbar_color: "#121212"`
- `show_title: true`
- `url_bar_hiding: true`

The generated Android resources are created during the GitHub Actions build, so the Android source does not need to be edited for each website.
