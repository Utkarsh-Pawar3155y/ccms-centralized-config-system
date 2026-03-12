import axios from "axios";
import type { Config, CreateConfigPayload, UpdateConfigPayload } from "@/types/config";

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

export const configApi = {
  /** Create a new configuration */
  create: (data: CreateConfigPayload) => {
    console.log("Sending config:", data);
    return api.post<Config>("/configs/", data).then((r) => r.data);
  },

  /** Get configs for a service + environment */
  getByServiceEnv: (service: string, environment: string) =>
    api.get<Config[]>(`/configs/${service}/${environment}`).then((r) => r.data),

  /** Update a config's value */
  update: (id: string, data: UpdateConfigPayload) =>
    api.put<Config>(`/configs/${id}`, data).then((r) => r.data),

  /** Delete a config */
  delete: (id: string) =>
    api.delete(`/configs/${id}`).then((r) => r.data),

  /** Get all configs (assumes an endpoint exists, falls back to empty) */
  getAll: () =>
    api.get<Config[]>("/configs").then((r) => r.data).catch(() => [] as Config[]),

  /** Get global config history */
  getHistory: () =>
    api.get<Config[]>("/configs/history").then((r) => r.data).catch(() => [] as Config[]),
};

export default api;
