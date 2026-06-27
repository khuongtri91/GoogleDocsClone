import GoogleIcon from "@mui/icons-material/Google";
import LogoutIcon from "@mui/icons-material/Logout";
import RefreshIcon from "@mui/icons-material/Refresh";
import {
  Alert,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Chip,
  CircularProgress,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import { AppButton } from "../../../components";

type AuthPanelProps = {
  email: string | null;
  error: string | null;
  loading: boolean;
  onRefresh: () => Promise<void>;
  onSignInWithGoogle: () => Promise<void>;
  onSignOut: () => Promise<void>;
};

export function AuthPanel({
  email,
  error,
  loading,
  onRefresh,
  onSignInWithGoogle,
  onSignOut,
}: AuthPanelProps) {
  const signedIn = Boolean(email);

  return (
    <Card
      variant="outlined"
      sx={{
        borderColor: "var(--color-border)",
        borderRadius: 2,
        boxShadow: "0 18px 60px var(--color-shadow)",
        width: "100%",
      }}
    >
      <CardHeader
        action={
          <Chip
            label={signedIn ? "Connected" : "OAuth"}
            size="small"
            color={signedIn ? "success" : "default"}
            variant={signedIn ? "filled" : "outlined"}
          />
        }
        title={
          <Typography variant="h5" component="h1">
            Sign in to your workspace
          </Typography>
        }
        subheader="Use your Google account to continue."
        sx={{ pb: 1 }}
      />

      <CardContent>
        <Stack spacing={2.5}>
          {loading ? (
            <Alert
              icon={<CircularProgress size={18} />}
              severity="info"
              variant="outlined"
            >
              Verifying your session
            </Alert>
          ) : null}

          {email ? (
            <Alert severity="success" variant="outlined">
              Authenticated as {email}
            </Alert>
          ) : null}

          {error ? (
            <Alert severity="error" variant="outlined">
              {error}
            </Alert>
          ) : null}

          <Divider />

          <Stack spacing={1.5}>
            {signedIn ? (
              <>
                <AppButton
                  fullWidth
                  size="large"
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  disabled={loading}
                  onClick={onRefresh}
                >
                  Refresh session
                </AppButton>
                <AppButton
                  fullWidth
                  size="large"
                  variant="contained"
                  color="inherit"
                  startIcon={<LogoutIcon />}
                  disabled={loading}
                  onClick={onSignOut}
                >
                  Sign out
                </AppButton>
              </>
            ) : (
              <AppButton
                fullWidth
                size="large"
                variant="contained"
                startIcon={<GoogleIcon />}
                disabled={loading}
                onClick={onSignInWithGoogle}
              >
                Continue with Google
              </AppButton>
            )}
          </Stack>
        </Stack>
      </CardContent>

      <CardActions
        sx={{
          borderTop: "1px solid var(--color-border)",
          color: "text.secondary",
          px: 3,
          py: 2,
        }}
      >
        <Typography variant="caption">
          Your account keeps documents and collaboration settings tied to you.
        </Typography>
      </CardActions>
    </Card>
  );
}
