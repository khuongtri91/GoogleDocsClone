import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import { useMemo } from "react";

import { AppContainers } from "./containers";

const readCssColor = (name: string) =>
  getComputedStyle(document.documentElement).getPropertyValue(name).trim();

function App() {
  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: "light",
          primary: {
            main: readCssColor("--color-primary"),
          },
          background: {
            default: readCssColor("--color-page-background"),
            paper: readCssColor("--color-surface"),
          },
          text: {
            primary: readCssColor("--color-text-primary"),
          },
        },
        shape: {
          borderRadius: 8,
        },
      }),
    [],
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppContainers />
    </ThemeProvider>
  );
}

export default App;
