import api from '@/lib/api';

export interface WordPressSite {
  id: string;
  site_url: string;
  site_name: string | null;
  mcp_token: string;
  is_active: boolean;
  created_at: string;
}

export async function registerWordPressSite(
  siteUrl: string,
  appUsername: string,
  appPassword: string
): Promise<WordPressSite> {
  const res = await api.post<WordPressSite>('/wordpress/sites', {
    site_url: siteUrl,
    app_username: appUsername,
    app_password: appPassword,
  });
  return res.data;
}

export async function listWordPressSites(): Promise<WordPressSite[]> {
  const res = await api.get<WordPressSite[]>('/wordpress/sites');
  return res.data;
}

export async function deleteWordPressSite(siteId: string): Promise<void> {
  await api.delete(`/wordpress/sites/${siteId}`);
}
