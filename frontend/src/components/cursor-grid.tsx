import { useEffect } from "react";
import { StyleSheet, View, useWindowDimensions } from "react-native";
import Animated, {
  Easing,
  useAnimatedStyle,
  useSharedValue,
  withDelay,
  withRepeat,
  withTiming,
} from "react-native-reanimated";

import { useTheme } from "@/src/theme";

// Shared prop interface — matches cursor-grid.web.tsx so both platforms
// accept the same props from callers. Native ignores web-only props.
export interface CursorGridProps {
  cellSize?: number;
  color?: string;
  radius?: number;
  falloff?: "linear" | "smooth" | "sharp";
  holdTime?: number;
  fadeDuration?: number;
  lineWidth?: number;
  maxOpacity?: number;
  fillOpacity?: number;
  gridOpacity?: number;
  cellRadius?: number;
  clickPulse?: boolean;
  pulseSpeed?: number;
}

/**
 * Native (iOS / Android) fallback for CursorGrid.
 * Uses React Native Animated values to produce a gentle pulsing grid
 * with a floating glow orb — no Canvas API required.
 * Accepts the same interface as the web version; unused props are ignored.
 */
export function CursorGrid({ color }: CursorGridProps = {}) {
  const { colors } = useTheme();
  const { width, height } = useWindowDimensions();
  const brand = color ?? colors.brand;

  // Overall grid opacity pulse
  const gridOpacity = useSharedValue(0.12);
  // Two independent orbs with staggered timing
  const orb1Opacity = useSharedValue(0.35);
  const orb2Opacity = useSharedValue(0.18);

  useEffect(() => {
    gridOpacity.value = withRepeat(
      withTiming(0.42, { duration: 2600, easing: Easing.inOut(Easing.sine) }),
      -1,
      true,
    );
    orb1Opacity.value = withRepeat(
      withTiming(0.65, { duration: 3400, easing: Easing.inOut(Easing.sine) }),
      -1,
      true,
    );
    orb2Opacity.value = withDelay(
      900,
      withRepeat(
        withTiming(0.4, { duration: 2800, easing: Easing.inOut(Easing.sine) }),
        -1,
        true,
      ),
    );
  }, [gridOpacity, orb1Opacity, orb2Opacity]);

  const gridStyle  = useAnimatedStyle(() => ({ opacity: gridOpacity.value }));
  const orb1Style  = useAnimatedStyle(() => ({ opacity: orb1Opacity.value }));
  const orb2Style  = useAnimatedStyle(() => ({ opacity: orb2Opacity.value }));

  const CELL   = 44;
  const columns = Math.ceil(width  / CELL) + 1;
  const rows    = Math.ceil(height / CELL) + 1;

  return (
    <View style={[StyleSheet.absoluteFill, { pointerEvents: "none" } as any]}>
      {/* Pulsing grid lines */}
      <Animated.View style={[StyleSheet.absoluteFill, gridStyle]}>
        <View style={styles.grid}>
          {Array.from({ length: columns * rows }).map((_, idx) => (
            <View
              key={idx}
              style={[styles.cell, { borderColor: brand + "28", width: CELL, height: CELL }]}
            />
          ))}
        </View>
      </Animated.View>

      {/* Primary glow orb — upper-left quadrant */}
      <Animated.View
        style={[
          styles.orb,
          orb1Style,
          {
            backgroundColor: brand + "22",
            width:  260,
            height: 260,
            borderRadius: 130,
            top:  height * 0.08,
            left: width  * 0.05,
          },
        ]}
      />

      {/* Secondary glow orb — lower-right quadrant */}
      <Animated.View
        style={[
          styles.orb,
          orb2Style,
          {
            backgroundColor: brand + "18",
            width:  190,
            height: 190,
            borderRadius: 95,
            bottom: height * 0.10,
            right:  width  * 0.08,
          },
        ]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  grid: { flexDirection: "row", flexWrap: "wrap" },
  cell: { borderRightWidth: 1, borderBottomWidth: 1 } as never,
  orb:  { position: "absolute" },
});