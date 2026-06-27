import { CircularProgress, Typography } from "@mui/material";

export function LoadingContainer() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-8">
      <div className="flex items-center gap-3">
        <CircularProgress size={22} />
        <Typography variant="body2" color="text.secondary">
          Loading
        </Typography>
      </div>
    </main>
  );
}
