package com.minecade.web2apk;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;

import androidx.annotation.Nullable;
import androidx.browser.customtabs.CustomTabsIntent;
import androidx.core.splashscreen.SplashScreen;

public final class MainActivity extends android.app.Activity {

    private boolean websiteLaunchAttempted;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        SplashScreen.installSplashScreen(this);
        super.onCreate(savedInstanceState);

        if (savedInstanceState == null) {
            openWebsite();
        }
    }

    private void openWebsite() {
        if (websiteLaunchAttempted) {
            return;
        }
        websiteLaunchAttempted = true;

        int resourceId = getResources().getIdentifier(
                "website_url",
                "string",
                getPackageName()
        );

        if (resourceId == 0) {
            return;
        }

        Uri uri = Uri.parse(getString(resourceId));
        CustomTabsIntent customTabsIntent = new CustomTabsIntent.Builder().build();

        try {
            customTabsIntent.launchUrl(this, uri);
        } catch (ActivityNotFoundException exception) {
            Intent fallback = new Intent(Intent.ACTION_VIEW, uri);
            startActivity(fallback);
        }

        // Do not finish this Activity. Keeping it alive preserves the app's
        // launcher task while the Custom Tab is displayed.
    }
}
