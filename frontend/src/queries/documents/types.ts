export type DocumentSummary = {
  id: string;
  title: string;
  owner_id: string;
  head_revision: number;
  updated_at: string;
};

export type DocumentDetail = DocumentSummary & {
  content: string;
};

export type CreateDocumentPayload = {
  title: string;
};

export type UpdateDocumentPayload = {
  title?: string;
  content?: string;
};
