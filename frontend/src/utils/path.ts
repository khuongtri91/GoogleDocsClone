export const PATHS = {
  home: "/",
  authCallback: "/auth/callback",
  documents: "/documents",
  documentDetail: "/documents/:documentId",
} as const;

export const buildDocumentPath = (documentId: string) =>
  `/documents/${documentId}`;
