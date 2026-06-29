import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import SaveIcon from "@mui/icons-material/Save";
import {
  Alert,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { AppButton } from "../../components";
import {
  useCreateDocument,
  useDeleteDocument,
  useGetDocument,
  useGetDocuments,
  useUpdateDocument,
} from "../../queries/documents";
import { PATHS, buildDocumentPath } from "../../utils/path";
import { TipTapDocumentEditor } from "./components";

const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function DocumentManagement() {
  const navigate = useNavigate();
  const { documentId } = useParams();
  const hasInvalidDocumentId = Boolean(documentId && !UUID_PATTERN.test(documentId));
  const documentsQuery = useGetDocuments();
  const documentQuery = useGetDocument(documentId ?? null, {
    enabled: !hasInvalidDocumentId,
  });
  const createDocumentMutation = useCreateDocument();
  const updateDocumentMutation = useUpdateDocument();
  const deleteDocumentMutation = useDeleteDocument();
  const [newTitle, setNewTitle] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  useEffect(() => {
    if (!documentId) {
      setTitle("");
      setContent("");
      return;
    }

    if (!documentQuery.data) {
      return;
    }

    setTitle(documentQuery.data.title);
    setContent(documentQuery.data.content);
  }, [documentId, documentQuery.data]);

  const selectedDocument = documentQuery.data;
  const currentError = useMemo(() => {
    const error =
      documentsQuery.error ??
      documentQuery.error ??
      createDocumentMutation.error ??
      updateDocumentMutation.error ??
      deleteDocumentMutation.error;

    return error instanceof Error ? error.message : null;
  }, [
    createDocumentMutation.error,
    deleteDocumentMutation.error,
    documentQuery.error,
    documentsQuery.error,
    updateDocumentMutation.error,
  ]);

  const createDocument = async () => {
    const trimmedTitle = newTitle.trim();

    if (!trimmedTitle) {
      return;
    }

    const createdDocument = await createDocumentMutation.mutateAsync({
      title: trimmedTitle,
    });
    setNewTitle("");
    navigate(buildDocumentPath(createdDocument.id));
  };

  const saveDocument = async () => {
    if (!selectedDocument) {
      return;
    }

    await updateDocumentMutation.mutateAsync({
      documentId: selectedDocument.id,
      payload: {
        title,
        content,
      },
    });
  };

  const deleteDocument = async () => {
    if (!selectedDocument) {
      return;
    }

    await deleteDocumentMutation.mutateAsync(selectedDocument.id);
    navigate(PATHS.documents, { replace: true });
  };

  return (
    <main className="min-h-screen bg-[var(--color-page-background)] px-6 py-8">
      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[320px_minmax(0,1fr)]">
        <aside>
          <Card variant="outlined" sx={{ borderColor: "var(--color-border)" }}>
            <CardContent>
              <Stack spacing={2}>
                <div>
                  <Typography variant="overline" color="text.secondary">
                    Workspace
                  </Typography>
                  <Typography variant="h6">Documents</Typography>
                </div>

                <Stack direction="row" spacing={1}>
                  <TextField
                    fullWidth
                    size="small"
                    label="New document"
                    value={newTitle}
                    onChange={(event) => setNewTitle(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        void createDocument();
                      }
                    }}
                  />
                  <Tooltip title="Create document">
                    <span>
                      <IconButton
                        color="primary"
                        disabled={
                          !newTitle.trim() || createDocumentMutation.isPending
                        }
                        onClick={() => void createDocument()}
                      >
                        <AddIcon />
                      </IconButton>
                    </span>
                  </Tooltip>
                </Stack>

                <Divider />

                {documentsQuery.isLoading ? (
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <CircularProgress size={18} />
                    <Typography variant="body2" color="text.secondary">
                      Loading documents
                    </Typography>
                  </Stack>
                ) : null}

                <List dense disablePadding>
                  {documentsQuery.data?.map((document) => (
                    <ListItem key={document.id} disablePadding>
                      <ListItemButton
                        component={Link}
                        selected={document.id === documentId}
                        to={buildDocumentPath(document.id)}
                      >
                        <ListItemText
                          primary={document.title}
                          secondary={`Revision ${document.head_revision}`}
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </Stack>
            </CardContent>
          </Card>
        </aside>

        <section>
          <Card variant="outlined" sx={{ borderColor: "var(--color-border)" }}>
            <CardContent>
              <Stack spacing={2.5}>
                {hasInvalidDocumentId ? (
                  <Alert
                    severity="warning"
                    variant="outlined"
                    action={
                      <AppButton
                        color="inherit"
                        size="small"
                        onClick={() => navigate(PATHS.documents, { replace: true })}
                      >
                        Back
                      </AppButton>
                    }
                  >
                    Invalid document URL.
                  </Alert>
                ) : null}

                {currentError && !hasInvalidDocumentId ? (
                  <Alert severity="error" variant="outlined">
                    {currentError}
                  </Alert>
                ) : null}

                {!documentId ? (
                  <Stack spacing={1}>
                    <Typography variant="h5">Select a document</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Create or open a document from the workspace list.
                    </Typography>
                  </Stack>
                ) : null}

                {documentQuery.isLoading ? (
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <CircularProgress size={18} />
                    <Typography variant="body2" color="text.secondary">
                      Opening document
                    </Typography>
                  </Stack>
                ) : null}

                {selectedDocument ? (
                  <>
                    <Stack
                      direction={{ xs: "column", md: "row" }}
                      spacing={1.5}
                      alignItems={{ xs: "stretch", md: "center" }}
                    >
                      <TextField
                        fullWidth
                        size="small"
                        label="Title"
                        value={title}
                        onChange={(event) => setTitle(event.target.value)}
                      />
                      <AppButton
                        variant="contained"
                        startIcon={<SaveIcon />}
                        disabled={updateDocumentMutation.isPending}
                        onClick={() => void saveDocument()}
                      >
                        Save
                      </AppButton>
                      <AppButton
                        variant="outlined"
                        color="error"
                        startIcon={<DeleteIcon />}
                        disabled={deleteDocumentMutation.isPending}
                        onClick={() => void deleteDocument()}
                      >
                        Delete
                      </AppButton>
                    </Stack>

                    <TipTapDocumentEditor
                      content={content}
                      onChange={setContent}
                    />
                  </>
                ) : null}
              </Stack>
            </CardContent>
          </Card>
        </section>
      </div>
    </main>
  );
}

export default DocumentManagement;
