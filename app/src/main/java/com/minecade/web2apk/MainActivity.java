package com.minecade.web2apk;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;

import androidx.annotation.Nullable;
import androidx.browser.customtabs.CustomTabsIntent;
import androidx.core.splashscreen.SplashScreen;

public final class MainActivity extends android.app.Activity {

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        SplashScreen.installSplashScreen(this);
        super.onCreate(savedInstanceState);
        openWebsite();
    }

    private void openWebsite() {
        Uri uri = Uri.parse(BuildConfig.WEBSITE_URL);

        CustomTabsIntent customTabsIntent = new CustomTabsIntent.Builder().build();

        try {
            customTabsIntent.launchUrl(this, uri);
        } catch (ActivityNotFoundException exception) {
            Intent fallback = new Intent(Intent.ACTION_VIEW, uri);
            startActivity(fallback);
        }

        finish();
    }
}
