import { config } from "../lib/config";

type HttpRequestOptions = RequestInit & {
  accessToken?: string;
};

const buildApiUrl = (path: string) => {
  const baseUrl = config.apiBaseUrl.replace(/\/$/, "");
  const normalizedPath = path.replace(/^\//, "");

  return `${baseUrl}/${normalizedPath}`;
};

const request = async <ResponseBody>(
  path: string,
  options: HttpRequestOptions = {},
): Promise<ResponseBody> => {
  const { accessToken, headers, ...requestOptions } = options;
  const requestHeaders = new Headers(headers);

  if (accessToken) {
    requestHeaders.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await fetch(buildApiUrl(path), {
    ...requestOptions,
    headers: requestHeaders,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as ResponseBody;
  }

  return response.json();
};

export const httpService = {
  get: <ResponseBody>(path: string, options?: HttpRequestOptions) =>
    request<ResponseBody>(path, {
      ...options,
      method: "GET",
    }),
};
