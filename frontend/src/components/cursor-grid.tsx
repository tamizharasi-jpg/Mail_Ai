import { useEffect } from "react";
import { StyleSheet, View, useWindowDimensions } from "react-native";
import Animated, { useAnimatedStyle, useSharedValue, withRepeat, withTiming } from "react-native-reanimated";

import { useTheme } from "@/src/theme";

export function CursorGrid() {
  const { colors } = useTheme();
  const { width, height } = useWindowDimensions();
  const pulse = useSharedValue(0.2);
  useEffect(() => { pulse.value = withRepeat(withTiming(0.72, { duration: 1800 }), -1, true); }, [pulse]);
  const animatedStyle = useAnimatedStyle(() => ({ opacity: pulse.value }));
  const columns = Math.ceil(width / 34) + 1;
  const rows = Math.ceil(height / 34) + 1;
  return (
    <Animated.View pointerEvents="none" style={[StyleSheet.absoluteFill, animatedStyle, { backgroundColor: colors.surface }]}>
      <View style={styles.grid}>
        {Array.from({ length: columns * rows }).map((_, index) => <View key={index} style={[styles.cell, { borderColor: colors.border, width: 34, height: 34 }]} />)}
      </View>
      <View style={[styles.orb, { backgroundColor: colors.brandTertiary, top: height * 0.22, left: width * 0.5 }]} />
    </Animated.View>
  );
}

const styles = StyleSheet.create({ grid: { flexDirection: "row", flexWrap: "wrap" }, cell: { borderRightWidth: 1, borderBottomWidth: 1 } as never, orb: { position: "absolute", width: 180, height: 180, borderRadius: 90, opacity: 0.7 } });