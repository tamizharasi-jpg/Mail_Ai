import { useMemo } from "react";
import { Appearance, StyleSheet, useColorScheme } from "react-native";

export type ColorScheme = "light" | "dark";

const dark = {
  surface: "#0E1116", onSurface: "#F0F4F8", surfaceSecondary: "#161B22", onSurfaceSecondary: "#C9D1D9", surfaceTertiary: "#21262D", onSurfaceTertiary: "#8B949E", surfaceInverse: "#F0F4F8", onSurfaceInverse: "#0E1116", muted: "#8B949E", brand: "#FF5722", onBrand: "#FFFFFF", brandPrimary: "#FF5722", onBrandPrimary: "#FFFFFF", brandSecondary: "#F4511E", onBrandSecondary: "#FFFFFF", brandTertiary: "#2A1810", onBrandTertiary: "#FFAB91", success: "#238636", onSuccess: "#FFFFFF", warning: "#D29922", onWarning: "#0E1116", error: "#F85149", onError: "#FFFFFF", info: "#388BFd", onInfo: "#FFFFFF", border: "#30363D", borderStrong: "#FF5722", divider: "#21262D",
};

const light = {
  surface: "#F7F8FA", onSurface: "#181B20", surfaceSecondary: "#FFFFFF", onSurfaceSecondary: "#343A40", surfaceTertiary: "#ECEFF1", onSurfaceTertiary: "#626A72", surfaceInverse: "#181B20", onSurfaceInverse: "#F7F8FA", muted: "#747C84", brand: "#E64A19", onBrand: "#FFFFFF", brandPrimary: "#E64A19", onBrandPrimary: "#FFFFFF", brandSecondary: "#F4511E", onBrandSecondary: "#FFFFFF", brandTertiary: "#FBE9E2", onBrandTertiary: "#A52F12", success: "#218739", onSuccess: "#FFFFFF", warning: "#A66B00", onWarning: "#FFFFFF", error: "#C9342D", onError: "#FFFFFF", info: "#2769A8", onInfo: "#FFFFFF", border: "#D9DEE3", borderStrong: "#E64A19", divider: "#E7EAED",
};

export type ThemeColors = typeof dark;
export const defaultScheme = "dark" satisfies ColorScheme;
export const themes: { light: ThemeColors; dark: ThemeColors } = { light, dark };

export function setColorScheme(scheme: ColorScheme | null) {
  Appearance.setColorScheme?.(scheme ?? "unspecified");
}

setColorScheme(null);

export function useTheme(): { scheme: ColorScheme; colors: ThemeColors } {
  const system = useColorScheme();
  const scheme: ColorScheme = system === "light" ? "light" : "dark";
  return { scheme, colors: themes[scheme] };
}

export function makeStyles<T extends StyleSheet.NamedStyles<T> | StyleSheet.NamedStyles<any>>(factory: (colors: ThemeColors) => T): () => T {
  return function useStyles(): T {
    const { colors } = useTheme();
    return useMemo(() => StyleSheet.create(factory(colors)), [colors]);
  };
}