export interface Config {
  id: string;
  service_name: string;
  environment: string;
  key: string;
  value: string;
  version: number;
  created_at?: string;
  updated_at?: string;
}

export interface CreateConfigPayload {
  service_name: string;
  environment: string;
  key: string;
  value: string;
}

export interface UpdateConfigPayload {
  value: string;
}
