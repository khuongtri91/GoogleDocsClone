import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createDocument,
  deleteDocument,
  getDocument,
  getDocuments,
  updateDocument,
} from "./api";
import type { CreateDocumentPayload, UpdateDocumentPayload } from "./types";

export const documentQueryKeys = {
  all: ["documents"] as const,
  list: () => [...documentQueryKeys.all, "list"] as const,
  detail: (documentId: string | null) =>
    [...documentQueryKeys.all, "detail", documentId] as const,
};

export const useGetDocuments = () =>
  useQuery({
    queryKey: documentQueryKeys.list(),
    queryFn: getDocuments,
  });

export const useGetDocument = (
  documentId: string | null,
  options: { enabled?: boolean } = {},
) =>
  useQuery({
    queryKey: documentQueryKeys.detail(documentId),
    queryFn: () => {
      if (!documentId) {
        throw new Error("Missing document id");
      }

      return getDocument(documentId);
    },
    enabled: Boolean(documentId) && (options.enabled ?? true),
  });

export const useCreateDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateDocumentPayload) => createDocument(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: documentQueryKeys.list() });
    },
  });
};

export const useUpdateDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      documentId,
      payload,
    }: {
      documentId: string;
      payload: UpdateDocumentPayload;
    }) => updateDocument(documentId, payload),
    onSuccess: (document) => {
      void queryClient.invalidateQueries({ queryKey: documentQueryKeys.list() });
      queryClient.setQueryData(documentQueryKeys.detail(document.id), document);
    },
  });
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) => deleteDocument(documentId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: documentQueryKeys.list() });
    },
  });
};
