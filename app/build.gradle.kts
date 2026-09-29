plugins {
    id("com.android.application")
}

val appVersion = providers.gradleProperty("web2apk.version").orElse("1.0.0")
val packageSuffix = providers.gradleProperty("web2apk.packageSuffix").orElse("website")

android {
    namespace = "com.minecade.web2apk"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.minecade.${packageSuffix.get()}"
        minSdk = 23
        targetSdk = 36
        versionCode = providers.gradleProperty("web2apk.versionCode").orElse("1000000").get().toInt()
        versionName = appVersion.get()
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
            isMinifyEnabled = false
            isShrinkResources = false
        }
        release {
            isMinifyEnabled = false
            isShrinkResources = false
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation("androidx.browser:browser:1.10.0")
    implementation("androidx.core:core-splashscreen:1.2.0")
}
