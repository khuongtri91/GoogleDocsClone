import { getAccessToken, httpService } from "../../utils";
import type {
  CreateDocumentPayload,
  DocumentDetail,
  DocumentSummary,
  UpdateDocumentPayload,
} from "./types";

const jsonHeaders = {
  "Content-Type": "application/json",
};

export const getDocuments = async (): Promise<DocumentSummary[]> =>
  httpService.get<DocumentSummary[]>("/documents", {
    accessToken: await getAccessToken(),
  });

export const createDocument = async (
  payload: CreateDocumentPayload,
): Promise<DocumentDetail> =>
  httpService.post<DocumentDetail>("/documents", {
    accessToken: await getAccessToken(),
    body: JSON.stringify(payload),
    headers: jsonHeaders,
  });

export const getDocument = async (
  documentId: string,
): Promise<DocumentDetail> =>
  httpService.get<DocumentDetail>(`/documents/${documentId}`, {
    accessToken: await getAccessToken(),
  });

export const updateDocument = async (
  documentId: string,
  payload: UpdateDocumentPayload,
): Promise<DocumentDetail> =>
  httpService.patch<DocumentDetail>(`/documents/${documentId}`, {
    accessToken: await getAccessToken(),
    body: JSON.stringify(payload),
    headers: jsonHeaders,
  });

export const deleteDocument = async (documentId: string): Promise<void> =>
  httpService.delete<void>(`/documents/${documentId}`, {
    accessToken: await getAccessToken(),
  });
