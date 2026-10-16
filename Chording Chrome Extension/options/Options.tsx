import { useState } from "react";
import {
  Alert, Box, Button, Container, Dialog, DialogActions, DialogContent, DialogContentText,
  DialogTitle, FormControl, FormControlLabel, IconButton, InputLabel, LinearProgress,
  MenuItem, Paper, Select, Snackbar, Stack, Switch, TextField, Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { useSettings } from "../shared/useSettings.ts";
import { validateRules, type ShorthandRule } from "../shared/settings.ts";

export default function Options() {
  const { settings, error, busy, save, reload } = useSettings();
  const [pattern, setPattern] = useState("");
  const [replacement, setReplacement] = useState("");
  const [editing, setEditing] = useState<number | null>(null);
  const [editContext, setEditContext] = useState<{ profileId: string; rules: ShorthandRule[] } | null>(null);
  const [validation, setValidation] = useState("");
  const [profileName, setProfileName] = useState("");
  const [creating, setCreating] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [notice, setNotice] = useState("");
  const profile = settings?.profiles.find(p => p.id === settings.activeProfileId);

  function resetForm() { setPattern(""); setReplacement(""); setEditing(null); setEditContext(null); setValidation(""); }
  async function updateRules(rules: ShorthandRule[], message: string) {
    if (!profile) return false;
    const ok = await save({ type: "UPDATE_PROFILE_RULES", profileId: profile.id, rules, expectedRules: profile.rules });
    if (ok) setNotice(message);
    return ok;
  }
  async function submitShortcut(event: React.FormEvent) {
    event.preventDefault();
    if (!profile) return;
    if (editing !== null && (editContext?.profileId !== profile.id ||
        JSON.stringify(editContext.rules) !== JSON.stringify(profile.rules))) {
      setValidation("This profile changed in another window. Cancel editing and choose the shortcut again.");
      return;
    }
    const rule = { pattern: pattern.trim(), replacement };
    const rules = editing === null ? [...profile.rules, rule] : profile.rules.map((r, i) => i === editing ? rule : r);
    try { validateRules(rules); setValidation(""); }
    catch (cause) { setValidation((cause as Error).message); return; }
    if (await updateRules(rules, editing === null ? "Shortcut added." : "Shortcut updated.")) resetForm();
  }
  if (!settings) return <Container maxWidth="md" sx={{ py: 6 }}>
    <Typography variant="h4" component="h1">ChordScribe</Typography>
    {error ? <Alert severity="error" action={<Button onClick={() => void reload()}>Retry</Button>}>{error}</Alert>
      : <Box sx={{ mt: 3 }}><LinearProgress aria-label="Loading settings" /><Typography sx={{ mt: 2 }}>Loading your profiles…</Typography></Box>}
  </Container>;

  return <Container maxWidth="md" sx={{ py: { xs: 3, sm: 6 } }}>
    <Stack spacing={4}>
      <Box>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 650 }}>ChordScribe</Typography>
        <Typography color="text.secondary" sx={{ mt: 1, maxWidth: "65ch" }}>
          Your words, with fewer keystrokes. Set up shortcuts for the phrases you use often.
        </Typography>
      </Box>
      {error && <Alert severity="error" action={<Button onClick={() => void reload()}>Reload</Button>}>{error}</Alert>}
      <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 } }}>
        <Stack spacing={3}>
          <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" alignItems={{ xs: "flex-start", sm: "center" }}>
            <Box>
              <Typography variant="h6" component="h2">Typing shortcuts</Typography>
              <Typography color="text.secondary" variant="body2">
                {settings.isEnabled ? "Enabled in supported text fields." : "Paused. Your shortcuts are saved."}
              </Typography>
            </Box>
            <FormControlLabel label={settings.isEnabled ? "Enabled" : "Paused"} control={
              <Switch checked={settings.isEnabled} disabled={busy}
                onChange={(_, isEnabled) => void save({ type: "SET_ENABLED", isEnabled })} />
            } />
          </Stack>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <FormControl fullWidth size="small">
              <InputLabel id="profile-label">Active profile</InputLabel>
              <Select labelId="profile-label" label="Active profile" value={settings.activeProfileId} disabled={busy}
                onChange={async event => { if (await save({ type: "SET_ACTIVE_PROFILE", profileId: event.target.value })) resetForm(); }}>
                {settings.profiles.map(p => <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>)}
              </Select>
            </FormControl>
            <Button startIcon={<AddIcon />} sx={{ flexShrink: 0 }} onClick={() => setCreating(!creating)} disabled={busy}>
              {creating ? "Cancel new profile" : "New profile"}
            </Button>
          </Stack>
          {creating && <Box component="form" onSubmit={async event => {
            event.preventDefault();
            if (await save({ type: "CREATE_PROFILE", profileName })) {
              setProfileName(""); setCreating(false); resetForm(); setNotice("Profile created.");
            }
          }}>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField label="Profile name" size="small" autoFocus fullWidth value={profileName}
                onChange={event => setProfileName(event.target.value)} inputProps={{ maxLength: 80 }} disabled={busy} />
              <Button type="submit" variant="contained" disabled={busy || !profileName.trim()} sx={{ flexShrink: 0 }}>Create profile</Button>
            </Stack>
          </Box>}
        </Stack>
      </Paper>

      <Box component="section" aria-labelledby="shortcuts-title">
        <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={2} sx={{ mb: 2 }}>
          <Box sx={{ minWidth: 0 }}>
            <Typography id="shortcuts-title" variant="h6" component="h2" sx={{ overflowWrap: "anywhere" }}>{profile?.name} shortcuts</Typography>
            <Typography variant="body2" color="text.secondary">{profile?.rules.length || 0} saved · Saved when you add or update a shortcut</Typography>
          </Box>
          {profile?.id !== "default" && <Button color="error" disabled={busy} onClick={() => setDeleting(true)} sx={{ flexShrink: 0 }}>Delete profile</Button>}
        </Stack>
        {!profile?.rules.length ? <Box sx={{ py: 4, borderTop: 1, borderBottom: 1, borderColor: "divider" }}>
          <Typography>No shortcuts in this profile yet.</Typography>
          <Typography color="text.secondary" variant="body2" sx={{ mt: 0.5 }}>Add one below. Try “brb” → “be right back”.</Typography>
        </Box> : <Box component="ul" sx={{ listStyle: "none", m: 0, p: 0 }}>
          {profile.rules.map((rule, index) => <Box component="li" key={rule.pattern + index}
            sx={{ display: "flex", alignItems: "center", gap: 1, py: 1.5, borderTop: 1, borderColor: "divider" }}>
            <Box sx={{ flex: 1, minWidth: 0, display: "grid", gridTemplateColumns: { xs: "1fr", sm: "minmax(80px, 1fr) 3fr" }, gap: 1 }}>
              <Typography component="code" sx={{ fontFamily: "monospace", overflowWrap: "anywhere", color: "primary.dark" }}>{rule.pattern}</Typography>
              <Typography sx={{ overflowWrap: "anywhere", whiteSpace: "pre-wrap" }}>{rule.replacement}</Typography>
            </Box>
            <IconButton aria-label={"Edit shortcut " + rule.pattern} disabled={busy} onClick={() => {
              setPattern(rule.pattern); setReplacement(rule.replacement); setEditing(index); setValidation("");
              setEditContext({ profileId: profile.id, rules: structuredClone(profile.rules) });
              document.getElementById("shortcut-pattern")?.focus();
            }}><EditOutlinedIcon fontSize="small" /></IconButton>
            <IconButton aria-label={"Delete shortcut " + rule.pattern} disabled={busy}
              onClick={async () => { if (await updateRules(profile.rules.filter((_, i) => i !== index), "Shortcut deleted.")) resetForm(); }}>
              <DeleteOutlineIcon fontSize="small" />
            </IconButton>
          </Box>)}
        </Box>}

        <Box component="form" onSubmit={submitShortcut} sx={{ mt: 4 }}>
          <Typography component="h3" variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>{editing === null ? "Add a shortcut" : "Edit shortcut"}</Typography>
          {validation && <Alert severity="error" sx={{ mb: 2 }}>{validation}</Alert>}
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="flex-start">
            <TextField id="shortcut-pattern" label="Type this" size="small" value={pattern}
              onChange={event => setPattern(event.target.value)} helperText="One shortcut, no spaces" disabled={busy}
              sx={{ width: { xs: "100%", sm: 190 }, flexShrink: 0 }} inputProps={{ maxLength: 64 }} />
            <TextField label="Replace with" size="small" multiline minRows={1} maxRows={6} value={replacement}
              onChange={event => setReplacement(event.target.value)} helperText="The full word or phrase" disabled={busy}
              fullWidth inputProps={{ maxLength: 2000 }} />
            <Button type="submit" variant="contained" disabled={busy || !pattern.trim() || !replacement.trim()}
              sx={{ minHeight: 40, flexShrink: 0 }}>{busy ? "Saving…" : editing === null ? "Add shortcut" : "Save changes"}</Button>
          </Stack>
          {editing !== null && <Button sx={{ mt: 1 }} onClick={resetForm}>Cancel editing</Button>}
        </Box>
      </Box>
      <Box component="section" sx={{ borderTop: 1, borderColor: "divider", pt: 3 }}>
        <Typography component="h2" variant="subtitle1" sx={{ fontWeight: 600 }}>How to use your shortcuts</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, maxWidth: "70ch" }}>
          Type a shortcut, then a space or punctuation. Press Backspace immediately to undo the expansion.
          Shortcuts are case-sensitive and work in ordinary text inputs and text areas. Rich-text editors such as Google Docs are not supported.
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, maxWidth: "70ch" }}>
          Your profiles and shortcuts sync through Chrome. ChordScribe does not save the words you type or send page text to a server.
        </Typography>
      </Box>
    </Stack>
    <Dialog open={deleting} onClose={() => { if (!busy) setDeleting(false); }}>
      <DialogTitle>Delete {profile?.name}?</DialogTitle>
      <DialogContent><DialogContentText>This removes the profile and its {profile?.rules.length || 0} shortcuts. This cannot be undone.</DialogContentText></DialogContent>
      <DialogActions>
        <Button onClick={() => setDeleting(false)} disabled={busy}>Keep profile</Button>
        <Button color="error" disabled={busy} onClick={async () => {
          if (profile && await save({ type: "DELETE_PROFILE", profileId: profile.id })) {
            setDeleting(false); resetForm(); setNotice("Profile deleted.");
          }
        }}>Delete profile</Button>
      </DialogActions>
    </Dialog>
    <Snackbar open={!!notice} autoHideDuration={4000} onClose={() => setNotice("")} message={notice} />
  </Container>;
}
