import { createTheme } from "@mui/material/styles";
export const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#1976d2", dark: "#12549a" },
    background: { default: "#fafbfc", paper: "#ffffff" },
    text: { primary: "#19232e", secondary: "#526171" },
    divider: "#dce2e8",
  },
  typography: { fontFamily: '"Segoe UI", Roboto, Arial, sans-serif', button: { textTransform: "none", fontWeight: 600 } },
  shape: { borderRadius: 8 },
  components: {
    MuiButton: { defaultProps: { disableElevation: true }, styleOverrides: { root: { minHeight: 40 } } },
    MuiIconButton: { styleOverrides: { root: { minWidth: 40, minHeight: 40 } } },
    MuiCssBaseline: { styleOverrides: {
      "::selection": { background: "#d6e9fc", color: "#19232e" },
      ":focus-visible": { outline: "2px solid #12549a", outlineOffset: 3 },
      "input, textarea": { caretColor: "#12549a" },
    } },
  },
});
