import { MaterialCommunityIcons } from "@expo/vector-icons";
import * as Clipboard from "expo-clipboard";
import * as DocumentPicker from "expo-document-picker";
import { LinearGradient } from "expo-linear-gradient";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ActivityIndicator, KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { CursorGrid } from "@/src/components/cursor-grid";
import { RecordItem, analyzeEmail, analyzeFile, getHistory, saveFeedback } from "@/src/api";
import { makeStyles, useTheme } from "@/src/theme";
import { storage } from "@/src/utils/storage";

type Tab = "home" | "inbox" | "analyze" | "history";
type Filter = "all" | "priority" | "phishing" | "action";

const useStyles = makeStyles((c) => StyleSheet.create({
  root: { flex: 1, backgroundColor: c.surface }, safe: { flex: 1 }, content: { paddingHorizontal: 20, paddingTop: 18, paddingBottom: 28 },
  eyebrow: { color: c.brand, fontSize: 11, letterSpacing: 1.6, fontWeight: "800" }, h1: { color: c.onSurface, fontSize: 30, lineHeight: 35, fontWeight: "800" }, h2: { color: c.onSurface, fontSize: 21, fontWeight: "800" }, body: { color: c.onSurfaceSecondary, fontSize: 15, lineHeight: 22 }, muted: { color: c.muted, fontSize: 13, lineHeight: 19 },
  section: { marginTop: 28, marginBottom: 12, flexDirection: "row", alignItems: "center", justifyContent: "space-between" }, card: { backgroundColor: c.surfaceSecondary, borderWidth: 1, borderColor: c.border, borderRadius: 14, padding: 16 }, metricRow: { flexDirection: "row", gap: 10 }, metric: { flex: 1, minHeight: 92, justifyContent: "space-between" }, metricValue: { color: c.onSurface, fontSize: 28, fontWeight: "800", fontFamily: Platform.select({ ios: "Menlo", default: "monospace" }) }, metricLabel: { color: c.muted, fontSize: 11, fontWeight: "800", textTransform: "uppercase", letterSpacing: 0.7 },
  primary: { minHeight: 52, borderRadius: 12, backgroundColor: c.brandPrimary, alignItems: "center", justifyContent: "center", flexDirection: "row", gap: 9, paddingHorizontal: 18 }, primaryText: { color: c.onBrandPrimary, fontSize: 15, fontWeight: "800" }, secondary: { minHeight: 48, borderRadius: 12, borderWidth: 1, borderColor: c.border, alignItems: "center", justifyContent: "center", paddingHorizontal: 16, flexDirection: "row", gap: 8 }, secondaryText: { color: c.onSurface, fontSize: 14, fontWeight: "700" },
  input: { backgroundColor: c.surfaceTertiary, color: c.onSurface, borderRadius: 10, borderWidth: 1, borderColor: c.border, paddingHorizontal: 14, paddingVertical: 13, fontSize: 15, marginTop: 8 }, textArea: { minHeight: 180, textAlignVertical: "top" }, chipRow: { flexDirection: "row", gap: 8, paddingVertical: 2 }, chip: { minHeight: 38, paddingHorizontal: 14, borderRadius: 20, alignItems: "center", justifyContent: "center", borderWidth: 1, borderColor: c.border, backgroundColor: c.surfaceSecondary }, chipActive: { backgroundColor: c.brandTertiary, borderColor: c.borderStrong }, chipText: { color: c.onSurfaceSecondary, fontSize: 13, fontWeight: "700" }, chipTextActive: { color: c.onBrandTertiary },
  listCard: { marginBottom: 10, padding: 15 }, listTop: { flexDirection: "row", justifyContent: "space-between", gap: 10 }, listTitle: { color: c.onSurface, fontSize: 16, fontWeight: "800", flex: 1 }, listSender: { color: c.muted, fontSize: 13, marginTop: 4 }, listSummary: { color: c.onSurfaceSecondary, fontSize: 13, lineHeight: 18, marginTop: 12 }, badge: { borderRadius: 6, paddingHorizontal: 8, paddingVertical: 5, alignSelf: "flex-start" }, badgeText: { fontSize: 11, fontWeight: "800" }, nav: { borderTopWidth: 1, borderTopColor: c.divider, backgroundColor: c.surfaceSecondary, flexDirection: "row", paddingHorizontal: 8, paddingTop: 8 }, navItem: { flex: 1, alignItems: "center", minHeight: 58, gap: 4 }, navText: { fontSize: 11, fontWeight: "700" }, topBar: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }, iconButton: { width: 44, height: 44, borderRadius: 12, backgroundColor: c.surfaceTertiary, alignItems: "center", justifyContent: "center" }, divider: { height: 1, backgroundColor: c.divider, marginVertical: 16 }, progressTrack: { height: 7, backgroundColor: c.surfaceTertiary, borderRadius: 5, overflow: "hidden", marginTop: 12 }, progressFill: { height: "100%", backgroundColor: c.brandPrimary, borderRadius: 5 }, factorRow: { flexDirection: "row", alignItems: "flex-start", gap: 10, marginTop: 12 }, factorDot: { width: 8, height: 8, borderRadius: 4, marginTop: 6 }, entity: { backgroundColor: c.surfaceTertiary, borderRadius: 8, paddingHorizontal: 10, paddingVertical: 8, marginRight: 8, marginTop: 8 }, entityText: { color: c.onSurfaceSecondary, fontSize: 12 }, empty: { alignItems: "center", paddingVertical: 48 }, emptyIcon: { width: 56, height: 56, borderRadius: 28, backgroundColor: c.brandTertiary, alignItems: "center", justifyContent: "center", marginBottom: 14 }, error: { color: c.error, backgroundColor: c.surfaceTertiary, padding: 12, borderRadius: 10, marginTop: 12 },
}));

function Icon({ name, color, size = 20 }: { name: string; color: string; size?: number }) { return <MaterialCommunityIcons name={name as never} size={size} color={color} />; }

function StatusBadge({ label }: { label: string }) {
  const { colors } = useTheme();
  const color = label.includes("Phishing") || label === "Spam" ? colors.error : label === "Suspicious" || label === "Needs Review" ? colors.warning : label === "Legitimate" ? colors.success : colors.info;
  return <View style={[local.badge, { backgroundColor: `${color}22`, borderColor: color }]}><Text style={[local.badgeText, { color }]}>{label}</Text></View>;
}

export default function Index() {
  const styles = useStyles(); const insets = useSafeAreaInsets();
  const [started, setStarted] = useState(false); const [tab, setTab] = useState<Tab>("home"); const [clientId, setClientId] = useState("anonymous");
  const [history, setHistory] = useState<RecordItem[]>([]); const [detail, setDetail] = useState<RecordItem | null>(null); const [search, setSearch] = useState(""); const [error, setError] = useState("");
  const loadHistory = useCallback(async (query = "") => { if (clientId === "anonymous") return; try { setHistory(await getHistory(clientId, query)); setError(""); } catch (e) { setError(e instanceof Error ? e.message : "History is unavailable."); } }, [clientId]);
  useEffect(() => { (async () => { const saved = await storage.getItem("mailmind-client-id", ""); const id = saved || `client-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`; setClientId(id); await storage.setItem("mailmind-client-id", id); })(); }, []);
  useEffect(() => { if (started) void loadHistory(search); }, [started, search, loadHistory]);
  if (!started) return <StartScreen onStart={() => setStarted(true)} />;
  if (detail) return <DetailScreen item={detail} clientId={clientId} onBack={() => setDetail(null)} />;
  return <View style={styles.root}><View style={[styles.safe, { paddingTop: insets.top }]}>
    {tab === "home" && <HomeScreen history={history} onAnalyze={() => setTab("analyze")} onOpen={setDetail} />}
    {tab === "inbox" && <InboxScreen history={history} onOpen={setDetail} />}
    {tab === "analyze" && <AnalyzeScreen clientId={clientId} onComplete={(items) => { if (!items.length) return; setHistory((old) => [...items, ...old.filter((x) => !items.some((i) => i.id === x.id))]); setDetail(items[0]); }} />}
    {tab === "history" && <HistoryScreen history={history} search={search} setSearch={setSearch} onOpen={setDetail} error={error} />}
  </View><View style={[styles.nav, { paddingBottom: Math.max(insets.bottom, 8) }]}>
    <NavItem active={tab === "home"} label="Home" icon="view-dashboard-outline" onPress={() => setTab("home")} /><NavItem active={tab === "inbox"} label="Inbox" icon="inbox-arrow-down-outline" onPress={() => setTab("inbox")} /><NavItem active={tab === "analyze"} label="Analyze" icon="text-search" onPress={() => setTab("analyze")} /><NavItem active={tab === "history"} label="History" icon="history" onPress={() => setTab("history")} />
  </View></View>;
}

function StartScreen({ onStart }: { onStart: () => void }) {
  const styles = useStyles(); const { colors } = useTheme(); const insets = useSafeAreaInsets();

  // Glass-card style — backdrop-filter applied on web only
  const glassCard = useMemo(() => ({
    width: "100%" as const,
    maxWidth: 460,
    alignItems: "center" as const,
    backgroundColor: colors.surfaceSecondary + "E8",
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 24,
    paddingHorizontal: 28,
    paddingVertical: 36,
    overflow: "hidden" as const,
    ...(Platform.OS === "web"
      ? ({ backdropFilter: "blur(22px)", WebkitBackdropFilter: "blur(22px)" } as object)
      : {}),
  }), [colors]);

  return (
    <View style={[styles.root, { paddingTop: insets.top, paddingBottom: insets.bottom }]} testID="app-start">
      {/* Interactive canvas background (web) / pulsing grid (native) */}
      <CursorGrid
        color={colors.brand}
        cellSize={58}
        radius={190}
        maxOpacity={0.65}
        gridOpacity={0.05}
        fillOpacity={0.05}
        clickPulse
      />

      {/* Radial vignette: darken top + bottom edges for readability */}
      <LinearGradient
        colors={[colors.surface + "CC", "transparent", colors.surface + "CC"]}
        locations={[0, 0.45, 1]}
        style={[StyleSheet.absoluteFill, { pointerEvents: "none" }]}
      />

      {/* Hero glass card */}
      <View style={[start.content, { pointerEvents: "box-none" } as any]}>
        <View style={glassCard}>
          <View style={[start.mark, { borderColor: colors.brand + "55", backgroundColor: colors.brandTertiary }]}>
            <Icon name="radar" color={colors.brand} size={28} />
          </View>
          <Text style={[styles.eyebrow, { marginTop: 2 }]}>MAILMIND / INTELLIGENCE CONSOLE</Text>
          <Text style={[start.title, { color: colors.onSurface }]}>MailMind<Text style={{ color: colors.brand }}> AI</Text></Text>
          <Text style={[styles.body, start.subtitle]}>Understand your emails.{"\n"}Prioritize what matters. Respond intelligently.</Text>
          <View style={[start.status, { borderColor: colors.success + "55", backgroundColor: colors.success + "14" }]}>
            <View style={[start.live, { backgroundColor: colors.success }]} />
            <Text style={[styles.muted, { color: colors.success }]}>ML INFERENCE PIPELINE READY</Text>
          </View>
          <Pressable testID="start-button" accessibilityRole="button" onPress={onStart} style={({ pressed }) => [styles.primary, start.button, pressed && { opacity: 0.82, transform: [{ scale: 0.98 }] }]}>
            <Text style={styles.primaryText}>Start analyzing</Text>
            <Icon name="arrow-right" color={colors.onBrandPrimary} size={19} />
          </Pressable>
        </View>
      </View>

      <Text style={[styles.muted, start.footer]}>TF-IDF · FEATURE ENGINEERING · EXPLAINABLE AI</Text>
    </View>
  );
}

function NavItem({ active, label, icon, onPress }: { active: boolean; label: string; icon: string; onPress: () => void }) { const { colors } = useTheme(); return <Pressable testID={`nav-${label.toLowerCase()}`} accessibilityRole="tab" onPress={onPress} style={({ pressed }) => [local.navItem, pressed && { opacity: 0.65 }]}><Icon name={icon} color={active ? colors.brand : colors.muted} size={22} /><Text style={[local.navText, { color: active ? colors.brand : colors.muted }]}>{label}</Text></Pressable>; }

function HomeScreen({ history, onAnalyze, onOpen }: { history: RecordItem[]; onAnalyze: () => void; onOpen: (item: RecordItem) => void }) {
  const styles = useStyles(); const { colors } = useTheme(); const stats = useMemo(() => ({ total: history.length, threat: history.filter((x) => ["Spam", "Suspicious", "Phishing Risk"].includes(x.analysis.spam.label)).length, priority: history.filter((x) => ["Critical", "High"].includes(x.analysis.priority.label)).length, action: history.filter((x) => x.analysis.intent.actionRequired).length }), [history]);
  return <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}><View style={styles.topBar}><View><Text style={styles.eyebrow}>MAILMIND / COMMAND CENTER</Text><Text style={[styles.h1, { marginTop: 6 }]}>Your signal,<Text style={{ color: colors.brand }}> clarified.</Text></Text></View><View style={styles.iconButton}><Icon name="radar" color={colors.brand} size={22} /></View></View><Text style={styles.body}>A data-driven view of what needs your attention.</Text>
    <View style={styles.section}><Text style={styles.h2}>At a glance</Text><Text style={styles.muted}>LIVE MEMORY</Text></View><View style={styles.metricRow}><View style={[styles.card, styles.metric]}><Text style={styles.metricValue}>{stats.total}</Text><Text style={styles.metricLabel}>Analyzed</Text></View><View style={[styles.card, styles.metric]}><Text style={[styles.metricValue, { color: colors.error }]}>{stats.threat}</Text><Text style={styles.metricLabel}>Threats</Text></View><View style={[styles.card, styles.metric]}><Text style={[styles.metricValue, { color: colors.warning }]}>{stats.priority}</Text><Text style={styles.metricLabel}>Priority</Text></View></View>
    <Pressable testID="home-analyze" onPress={onAnalyze} style={({ pressed }) => [styles.card, { marginTop: 18, borderColor: colors.borderStrong, backgroundColor: colors.brandTertiary }, pressed && { opacity: 0.8 }]}><Text style={styles.eyebrow}>RUN THE PIPELINE</Text><Text style={[styles.h2, { marginTop: 8 }]}>Analyze a new email</Text><Text style={[styles.body, { marginTop: 6 }]}>Paste a message or send an email file through NLP and ML.</Text><View style={[styles.primary, { marginTop: 16 }]}><Text style={styles.primaryText}>Open analyzer</Text><Icon name="arrow-right" color={colors.onBrandPrimary} /></View></Pressable>
    <View style={styles.section}><Text style={styles.h2}>Recent signals</Text><Pressable onPress={() => history[0] && onOpen(history[0])}><Text style={[styles.muted, { color: colors.brand }]}>VIEW ALL</Text></Pressable></View>{history.slice(0, 3).map((item) => <EmailRow key={item.id} item={item} onPress={() => onOpen(item)} />)}{history.length === 0 && <EmptyState title="No analysis records yet" body="Your analyzed emails will appear here." />}
  </ScrollView>;
}

function InboxScreen({ history, onOpen }: { history: RecordItem[]; onOpen: (item: RecordItem) => void }) {
  const styles = useStyles(); const [filter, setFilter] = useState<Filter>("all"); const filtered = history.filter((item) => filter === "all" || (filter === "priority" && ["Critical", "High"].includes(item.analysis.priority.label)) || (filter === "phishing" && ["Suspicious", "Phishing Risk", "Spam"].includes(item.analysis.spam.label)) || (filter === "action" && item.analysis.intent.actionRequired));
  return <ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>MAILMIND / INBOX</Text><Text style={[styles.h1, { marginTop: 6 }]}>Triage your stream</Text><Text style={[styles.body, { marginTop: 8 }]}>Every message has a signal. Start with the outliers.</Text><ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginTop: 22 }} contentContainerStyle={styles.chipRow}>{([["all", "All"], ["priority", "Priority"], ["phishing", "Security"], ["action", "Action"]] as [Filter, string][]).map(([key, label]) => <Pressable testID={`filter-${key}`} key={key} onPress={() => setFilter(key)} style={[styles.chip, filter === key && styles.chipActive]}><Text style={[styles.chipText, filter === key && styles.chipTextActive]}>{label}</Text></Pressable>)}</ScrollView><View style={{ marginTop: 18 }}>{filtered.map((item) => <EmailRow key={item.id} item={item} onPress={() => onOpen(item)} />)}{filtered.length === 0 && <EmptyState title="Inbox is clear" body="Analyze an email to populate your intelligence stream." />}</View></ScrollView>;
}

function HistoryScreen({ history, search, setSearch, onOpen, error }: { history: RecordItem[]; search: string; setSearch: (v: string) => void; onOpen: (item: RecordItem) => void; error: string }) { const styles = useStyles(); return <ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>MAILMIND / HISTORY</Text><Text style={[styles.h1, { marginTop: 6 }]}>Analysis log</Text><TextInput testID="history-search" value={search} onChangeText={setSearch} placeholder="Search subject or sender" placeholderTextColor={styles.muted.color} style={styles.input} /><Text style={[styles.muted, { marginTop: 16 }]}>{history.length} stored analysis records</Text>{error ? <Text testID="history-error" style={styles.error}>{error}</Text> : null}<View style={{ marginTop: 16 }}>{history.map((item) => <EmailRow key={item.id} item={item} onPress={() => onOpen(item)} />)}{history.length === 0 && <EmptyState title="No history yet" body="Completed analyses are saved locally to your intelligence log." />}</View></ScrollView>; }

function EmailRow({ item, onPress }: { item: RecordItem; onPress: () => void }) { const styles = useStyles(); const { colors } = useTheme(); return <Pressable testID={`email-row-${item.id}`} onPress={onPress} style={({ pressed }) => [styles.card, styles.listCard, pressed && { opacity: 0.78 }]}><View style={styles.listTop}><View style={{ flex: 1 }}><Text style={styles.listTitle} numberOfLines={1}>{item.subject || "Untitled email"}</Text><Text style={styles.listSender} numberOfLines={1}>{item.sender || "Unknown sender"}</Text></View><StatusBadge label={item.analysis.spam.label} /></View><Text style={styles.listSummary} numberOfLines={2}>{item.analysis.summary || "Structured analysis available."}</Text><View style={{ flexDirection: "row", gap: 8, marginTop: 12 }}><Text style={[styles.muted, { color: item.analysis.priority.label === "Critical" ? colors.error : colors.muted }]}>{item.analysis.priority.label} priority</Text><Text style={styles.muted}>·</Text><Text style={styles.muted}>{item.analysis.category.label}</Text></View></Pressable>; }

function EmptyState({ title, body }: { title: string; body: string }) { const styles = useStyles(); const { colors } = useTheme(); return <View style={styles.empty}><View style={styles.emptyIcon}><Icon name="email-outline" color={colors.brand} size={25} /></View><Text style={styles.h2}>{title}</Text><Text style={[styles.body, { textAlign: "center", marginTop: 8, maxWidth: 280 }]}>{body}</Text></View>; }

const local = StyleSheet.create({ badge: { borderWidth: 1, borderRadius: 6, paddingHorizontal: 8, paddingVertical: 5 }, badgeText: { fontSize: 11, fontWeight: "800" }, navItem: { flex: 1, alignItems: "center", minHeight: 58, gap: 4 }, navText: { fontSize: 11, fontWeight: "700" } });
const start = StyleSheet.create({
  content:  { flex: 1, alignItems: "center", justifyContent: "center", paddingHorizontal: 20 },
  mark:     { width: 66, height: 66, borderWidth: 1, borderRadius: 18, alignItems: "center", justifyContent: "center", marginBottom: 20 },
  title:    { fontSize: 52, fontWeight: "900", letterSpacing: -2, marginTop: 10 },
  subtitle: { textAlign: "center", marginTop: 14, lineHeight: 24 },
  status:   { flexDirection: "row", alignItems: "center", gap: 8, borderWidth: 1, borderRadius: 20, paddingHorizontal: 14, paddingVertical: 9, marginTop: 26 },
  live:     { width: 7, height: 7, borderRadius: 4 },
  button:   { width: "100%", marginTop: 30 },
  footer:   { textAlign: "center", letterSpacing: 1, marginBottom: 14 },
});

function AnalyzeScreen({ clientId, onComplete }: { clientId: string; onComplete: (items: RecordItem[]) => void }) {
  const styles = useStyles(); const { colors } = useTheme(); const [mode, setMode] = useState<"paste" | "file">("paste"); const [sender, setSender] = useState(""); const [subject, setSubject] = useState(""); const [body, setBody] = useState(""); const [loading, setLoading] = useState(false); const [progress, setProgress] = useState({ done: 0, total: 0, emails: 0 }); const [error, setError] = useState(""); const [summary, setSummary] = useState("");
  const submit = async () => { if (!subject.trim() && !body.trim()) { setError("Add a subject or body before running analysis."); return; } setLoading(true); setError(""); setSummary(""); try { const item = await analyzeEmail({ sender, subject, body, client_id: clientId, source_name: "pasted-email" }); onComplete([item]); } catch (e) { setError(e instanceof Error ? e.message : "Analysis failed. Please try again."); } finally { setLoading(false); } };
  const pickFiles = async () => { const picked = await DocumentPicker.getDocumentAsync({ multiple: true, copyToCacheDirectory: true, type: ["message/rfc822", "text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/csv", "application/csv"] }); if (picked.canceled) return; setLoading(true); setError(""); setSummary(""); setProgress({ done: 0, total: picked.assets.length, emails: 0 }); const results: RecordItem[] = []; const errors: string[] = []; for (const asset of picked.assets) { try { const batch = await analyzeFile(asset, clientId); results.push(...batch.items); setProgress((old) => ({ done: old.done + 1, total: old.total, emails: old.emails + batch.items.length })); } catch (e) { errors.push(`${asset.name}: ${e instanceof Error ? e.message : "unreadable"}`); setProgress((old) => ({ ...old, done: old.done + 1 })); } } setLoading(false); if (errors.length) setError(errors.join("\n")); if (results.length) { setSummary(`${results.length} email${results.length === 1 ? "" : "s"} processed from ${picked.assets.length} file${picked.assets.length === 1 ? "" : "s"}`); onComplete(results); } };
  return <KeyboardAvoidingView style={styles.root} behavior={Platform.OS === "ios" ? "padding" : "height"}><ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled"><Text style={styles.eyebrow}>MAILMIND / ANALYZE</Text><Text style={[styles.h1, { marginTop: 6 }]}>Open the signal</Text><Text style={[styles.body, { marginTop: 8 }]}>Run cleaning, feature extraction, classification, and explainability in one pass.</Text><View style={[styles.chipRow, { marginTop: 22 }]}><Pressable testID="mode-paste" onPress={() => setMode("paste")} style={[styles.chip, mode === "paste" && styles.chipActive]}><Text style={[styles.chipText, mode === "paste" && styles.chipTextActive]}>Paste email</Text></Pressable><Pressable testID="mode-file" onPress={() => setMode("file")} style={[styles.chip, mode === "file" && styles.chipActive]}><Text style={[styles.chipText, mode === "file" && styles.chipTextActive]}>Upload files</Text></Pressable></View>{mode === "paste" ? <><TextInput testID="sender-input" value={sender} onChangeText={setSender} placeholder="Sender email (optional)" placeholderTextColor={colors.muted} autoCapitalize="none" style={styles.input} /><TextInput testID="subject-input" value={subject} onChangeText={setSubject} placeholder="Subject" placeholderTextColor={colors.muted} style={styles.input} /><TextInput testID="body-input" value={body} onChangeText={setBody} placeholder="Paste the full email body here" placeholderTextColor={colors.muted} multiline style={[styles.input, styles.textArea]} /><View style={[styles.card, { marginTop: 16 }]}><Text style={styles.eyebrow}>PIPELINE</Text><Text style={[styles.body, { marginTop: 8 }]}>HTML cleaning · TF-IDF n-grams · phishing signals · model factors · response assistance</Text></View><Pressable testID="run-analysis" disabled={loading} onPress={submit} style={({ pressed }) => [styles.primary, { marginTop: 18 }, pressed && { opacity: 0.8 }, loading && { opacity: 0.55 }]}>{loading ? <ActivityIndicator color={colors.onBrandPrimary} /> : <><Text style={styles.primaryText}>Run ML analysis</Text><Icon name="play" color={colors.onBrandPrimary} /></>}</Pressable></> : <><Pressable testID="file-picker" disabled={loading} onPress={pickFiles} style={({ pressed }) => [styles.card, { marginTop: 18, minHeight: 200, alignItems: "center", justifyContent: "center", borderStyle: "dashed", borderColor: colors.brand }, pressed && { opacity: 0.76 }]}><Icon name="file-upload-outline" color={colors.brand} size={38} /><Text style={[styles.h2, { marginTop: 14 }]}>Choose email files</Text><Text style={[styles.body, { textAlign: "center", marginTop: 6 }]}>.eml · .txt · .pdf · .docx · .csv{ "\n" }Multiple emails per file supported</Text><Text style={[styles.muted, { textAlign: "center", marginTop: 8 }]}>Up to 50 files, 8 MB each</Text></Pressable>{loading && <View testID="batch-progress" style={{ marginTop: 20 }}><Text style={styles.muted}>Analyzing file {progress.done}/{progress.total} · {progress.emails} email{progress.emails === 1 ? "" : "s"} processed</Text><View style={styles.progressTrack}><View style={[styles.progressFill, { width: `${progress.total ? (progress.done / progress.total) * 100 : 0}%` }]} /></View></View>}{summary ? <Text testID="batch-summary" style={[styles.muted, { marginTop: 16, color: colors.success }]}>{summary}</Text> : null}</>}{error ? <Text testID="analysis-error" style={styles.error}>{error}</Text> : null}</ScrollView></KeyboardAvoidingView>;
}

function DetailScreen({ item, clientId, onBack }: { item: RecordItem; clientId: string; onBack: () => void }) {
  const styles = useStyles(); const { colors } = useTheme(); const insets = useSafeAreaInsets(); const a = item.analysis; const [feedback, setFeedback] = useState("");
  const sendFeedback = async (field: string, value: string) => { try { await saveFeedback(item.id, clientId, field, value); setFeedback("Correction saved"); } catch { setFeedback("Could not save correction"); } };
  return <View style={styles.root}><ScrollView contentContainerStyle={[styles.content, { paddingTop: insets.top + 14, paddingBottom: insets.bottom + 28 }]}><View style={styles.topBar}><Pressable testID="detail-back" onPress={onBack} style={styles.iconButton}><Icon name="arrow-left" color={colors.onSurface} /></Pressable><Text style={styles.eyebrow}>EXPLAINABLE ANALYSIS</Text><View style={{ width: 44 }} /></View><Text style={styles.h1} numberOfLines={2}>{item.subject || "Untitled email"}</Text><Text style={[styles.muted, { marginTop: 7 }]}>{item.sender || "Unknown sender"} · {item.source_name}</Text><View style={[styles.card, { marginTop: 20, borderColor: a.spam.label === "Legitimate" ? colors.success : colors.warning }]}><View style={styles.listTop}><View><Text style={styles.eyebrow}>CLASSIFICATION</Text><Text style={[styles.h2, { marginTop: 7 }]}>{a.spam.label}</Text></View><StatusBadge label={a.priority.label} /></View><Text style={[styles.body, { marginTop: 12 }]}>{a.summary}</Text><View style={styles.divider} /><ProbRow label="Spam probability" value={a.spam.probability} color={a.spam.label === "Legitimate" ? colors.success : colors.error} /><ProbRow label="Phishing supporting signal" value={a.phishing.probability} color={colors.warning} /><ProbRow label="Category confidence" value={a.category.probability} color={colors.brand} /></View><View style={styles.section}><Text style={styles.h2}>Factors that influenced the model</Text></View><View style={styles.card}>{a.explanation.map((factor, index) => <View key={`${factor.text}-${index}`} style={styles.factorRow}><View style={[styles.factorDot, { backgroundColor: factor.direction === "risk" ? colors.warning : colors.success }]} /><Text style={[styles.body, { flex: 1 }]}>{factor.text}</Text></View>)}</View><View style={styles.section}><Text style={styles.h2}>Decision context</Text></View><View style={styles.card}><InfoLine label="Category" value={a.category.label} /><InfoLine label="Priority" value={a.priority.label} /><InfoLine label="Intent" value={a.intent.label} /><InfoLine label="Action required" value={a.intent.actionRequired ? "Yes" : "No"} />{a.priority.reasons?.map((reason) => <Text key={reason} style={[styles.muted, { marginTop: 9 }]}>· {reason}</Text>)}</View><View style={styles.section}><Text style={styles.h2}>Extracted information</Text></View><View style={styles.card}>{Object.entries(a.entities).map(([key, values]) => values.length ? <View key={key} style={{ marginBottom: 8 }}><Text style={styles.eyebrow}>{key.toUpperCase()}</Text><View style={{ flexDirection: "row", flexWrap: "wrap" }}>{values.map((value) => <View key={value} style={styles.entity}><Text style={styles.entityText}>{value}</Text></View>)}</View></View> : null)}</View>{a.responseRecommendation ? <><View style={styles.section}><Text style={styles.h2}>Response assistant</Text></View><View style={[styles.card, { borderColor: colors.brand }]}><Text style={styles.body}>{a.responseRecommendation}</Text>{a.suggestedResponse ? <><Text style={[styles.eyebrow, { marginTop: 18 }]}>SUGGESTED DRAFT</Text><Text style={[styles.body, { marginTop: 8 }]}>{a.suggestedResponse}</Text><Pressable testID="copy-draft" onPress={() => { void Clipboard.setStringAsync(a.suggestedResponse); setFeedback("Draft copied"); }} style={[styles.secondary, { marginTop: 14 }]}><Icon name="content-copy" color={colors.onSurface} /><Text style={styles.secondaryText}>Copy draft</Text></Pressable></> : null}</View></> : null}<View style={styles.section}><Text style={styles.h2}>Correct this prediction</Text></View><View style={styles.card}><Text style={styles.muted}>Your corrections are saved as feedback for future model improvement.</Text><View style={{ flexDirection: "row", gap: 8, marginTop: 14 }}><Pressable testID="feedback-not-spam" onPress={() => void sendFeedback("spam", "Legitimate")} style={styles.secondary}><Text style={styles.secondaryText}>Not spam</Text></Pressable><Pressable testID="feedback-spam" onPress={() => void sendFeedback("spam", "Spam")} style={styles.secondary}><Text style={styles.secondaryText}>Spam</Text></Pressable></View>{feedback ? <Text testID="feedback-status" style={[styles.muted, { color: colors.success, marginTop: 12 }]}>{feedback}</Text> : null}</View><Text style={[styles.muted, { marginTop: 18, textAlign: "center" }]}>Model {a.modelVersion} · Estimates are not proof of malicious intent.</Text></ScrollView></View>;
}

function ProbRow({ label, value, color }: { label: string; value: number; color: string }) { const styles = useStyles(); return <View style={{ marginTop: 10 }}><View style={styles.listTop}><Text style={styles.muted}>{label}</Text><Text style={[styles.muted, { color, fontWeight: "800" }]}>{Math.round(value * 100)}%</Text></View><View style={styles.progressTrack}><View style={[styles.progressFill, { width: `${Math.round(value * 100)}%`, backgroundColor: color }]} /></View></View>; }
function InfoLine({ label, value }: { label: string; value: string }) { const styles = useStyles(); return <View style={{ flexDirection: "row", justifyContent: "space-between", paddingVertical: 7 }}><Text style={styles.muted}>{label}</Text><Text style={[styles.body, { fontWeight: "800" }]}>{value}</Text></View>; }