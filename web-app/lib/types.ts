export type Document = {
  document_number: string;
  title: string;
  publication_date: string;
  effective_on: string | null;
  abstract: string;
  agency_names: string[];
  html_url: string | null;
};

export type DocumentsResponse = {
  documents: Document[];
  offset: number;
  limit: number;
  total: number;
  next_offset: number | null;
};
