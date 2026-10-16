import { Alert, Box, Button, FormControl, FormControlLabel, InputLabel, LinearProgress, MenuItem, Select, Stack, Switch, Typography } from "@mui/material";
import { useSettings } from "../shared/useSettings.ts";
export default function Popup() {
  const { settings, error, busy, save, reload } = useSettings();
  const profile = settings?.profiles.find(p => p.id === settings.activeProfileId);
  return <Box sx={{ width: 340, p: 3 }}>
    <Stack spacing={2.5}>
      <Box><Typography component="h1" variant="h6" sx={{ fontWeight: 650 }}>ChordScribe</Typography>
        <Typography variant="body2" color="text.secondary">Your words, with fewer keystrokes.</Typography></Box>
      {error && <Alert severity="error" action={<Button onClick={() => void reload()}>Retry</Button>}>{error}</Alert>}
      {!settings ? !error && <LinearProgress aria-label="Loading settings" /> : <>
        <FormControlLabel label={settings.isEnabled ? "Shortcuts enabled" : "Shortcuts paused"} control={
          <Switch checked={settings.isEnabled} disabled={busy} onChange={(_, isEnabled) => void save({ type: "SET_ENABLED", isEnabled })} />
        } />
        <FormControl fullWidth size="small"><InputLabel id="popup-profile-label">Active profile</InputLabel>
          <Select labelId="popup-profile-label" label="Active profile" value={settings.activeProfileId} disabled={busy}
            onChange={event => void save({ type: "SET_ACTIVE_PROFILE", profileId: event.target.value })}>
            {settings.profiles.map(p => <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>)}
          </Select>
        </FormControl>
        <Typography variant="body2" color="text.secondary">{profile?.rules.length || 0} shortcuts in this profile.
          Type one, then a space. Backspace undoes the expansion.</Typography>
        <Button variant="contained" onClick={() => void chrome.runtime.openOptionsPage()}>Manage shortcuts</Button>
      </>}
    </Stack>
  </Box>;
}
