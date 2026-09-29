package com.minecade.web2apk;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.browser.customtabs.CustomTabColorSchemeParams;
import androidx.browser.customtabs.CustomTabsIntent;
import androidx.core.splashscreen.SplashScreen;

public final class MainActivity extends android.app.Activity {

    private boolean customTabLaunched;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        SplashScreen.installSplashScreen(this);
        super.onCreate(savedInstanceState);

        if (savedInstanceState == null) {
            openWebsite();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();

        // The Custom Tab is a separate activity. If the user closes it, finish
        // this launcher activity as well so Android Back never reveals a blank
        // Web2APK screen.
        if (customTabLaunched) {
            finish();
        }
    }

    private void openWebsite() {
        String websiteUrl = getString(R.string.website_url);
        Uri uri = Uri.parse(websiteUrl);

        CustomTabColorSchemeParams colorSchemeParams = new CustomTabColorSchemeParams.Builder()
                .setToolbarColor(getColor(R.color.toolbar_color))
                .build();

        CustomTabsIntent customTabsIntent = new CustomTabsIntent.Builder()
                .setShowTitle(getResources().getBoolean(R.bool.show_title))
                .setUrlBarHidingEnabled(getResources().getBoolean(R.bool.url_bar_hiding))
                .setDefaultColorSchemeParams(colorSchemeParams)
                .setCloseButtonPosition(CustomTabsIntent.CLOSE_BUTTON_POSITION_DEFAULT)
                .build();

        try {
            customTabLaunched = true;
            customTabsIntent.launchUrl(this, uri);
        } catch (ActivityNotFoundException exception) {
            Toast.makeText(
                    this,
                    "No browser supporting Custom Tabs is installed.",
                    Toast.LENGTH_LONG
            ).show();

            customTabLaunched = true;
            Intent fallback = new Intent(Intent.ACTION_VIEW, uri);
            try {
                startActivity(fallback);
            } catch (ActivityNotFoundException ignored) {
                Toast.makeText(
                        this,
                        "Unable to open the website.",
                        Toast.LENGTH_LONG
                ).show();
            }
        }
    }
}
