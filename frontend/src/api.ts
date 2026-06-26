const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

function getToken(): string | null {
  return localStorage.getItem("access_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${getToken()}`;
      const retry = await fetch(`${BASE}${path}`, { ...options, headers });
      if (!retry.ok) {
        const err = await retry.json().catch(() => ({ detail: retry.statusText }));
        throw new ApiError(retry.status, err.detail ?? "Request failed");
      }
      return retry.json();
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
    throw new ApiError(401, "Unauthorized");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, err.detail ?? "Request failed");
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function tryRefresh(): Promise<boolean> {
  const refresh = localStorage.getItem("refresh_token");
  if (!refresh) return false;
  try {
    const res = await fetch(`${BASE}/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

export async function signup(email: string, password: string) {
  const res = await request<{
    access_token: string;
    refresh_token: string;
  }>("/signup", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  localStorage.setItem("access_token", res.access_token);
  localStorage.setItem("refresh_token", res.refresh_token);
}

export async function login(email: string, password: string) {
  const res = await request<{
    access_token: string;
    refresh_token: string;
  }>("/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  localStorage.setItem("access_token", res.access_token);
  localStorage.setItem("refresh_token", res.refresh_token);
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
}

export async function getMe() {
  return request<{
    id: string;
    email: string;
    is_active: boolean;
    created_at: string;
  }>("/users/me");
}

export async function listOrgs() {
  return request<
    {
      id: string;
      name: string;
      slug: string;
      role: string;
      created_at: string;
    }[]
  >("/organizations");
}

export async function createOrg(name: string, slug: string) {
  return request<{
    id: string;
    name: string;
    slug: string;
    role: string;
    created_at: string;
  }>("/organizations", {
    method: "POST",
    body: JSON.stringify({ name, slug }),
  });
}

export async function getOrg(id: string) {
  return request<{
    id: string;
    name: string;
    slug: string;
    created_at: string;
  }>(`/organizations/${id}`);
}

export async function listMembers(orgId: string) {
  return request<
    {
      user_id: string;
      email: string;
      role: string;
      created_at: string;
    }[]
  >(`/organizations/${orgId}/members`);
}

export async function inviteMember(orgId: string, email: string, role: string) {
  return request<{ user_id: string; email: string; role: string }>(
    `/organizations/${orgId}/members`,
    {
      method: "POST",
      body: JSON.stringify({ email, role }),
    },
  );
}

export async function removeMember(orgId: string, userId: string) {
  return request<void>(`/organizations/${orgId}/members/${userId}`, {
    method: "DELETE",
  });
}

export async function listNotes(orgId: string) {
  return request<
    {
      id: string;
      org_id: string;
      title: string;
      body: string;
      created_by: string;
      created_at: string;
      updated_at: string;
    }[]
  >(`/organizations/${orgId}/notes`);
}

export async function createNote(
  orgId: string,
  title: string,
  body: string,
) {
  return request<{
    id: string;
    org_id: string;
    title: string;
    body: string;
    created_by: string;
    created_at: string;
    updated_at: string;
  }>(`/organizations/${orgId}/notes`, {
    method: "POST",
    body: JSON.stringify({ title, body }),
  });
}

export async function getNote(orgId: string, noteId: string) {
  return request<{
    id: string;
    org_id: string;
    title: string;
    body: string;
    created_by: string;
    created_at: string;
    updated_at: string;
  }>(`/organizations/${orgId}/notes/${noteId}`);
}

export async function updateNote(
  orgId: string,
  noteId: string,
  title: string,
  body: string,
) {
  return request<{
    id: string;
    org_id: string;
    title: string;
    body: string;
    created_by: string;
    created_at: string;
    updated_at: string;
  }>(`/organizations/${orgId}/notes/${noteId}`, {
    method: "PATCH",
    body: JSON.stringify({ title, body }),
  });
}

export async function deleteNote(orgId: string, noteId: string) {
  return request<void>(`/organizations/${orgId}/notes/${noteId}`, {
    method: "DELETE",
  });
}
