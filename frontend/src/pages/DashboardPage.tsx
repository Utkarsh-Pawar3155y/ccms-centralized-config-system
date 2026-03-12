import { Server, Settings2, Globe, Activity } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useEffect, useState } from "react";
import { configApi } from "@/services/api";
import type { Config } from "@/types/config";

const statCards = [
  { title: "Total Services", icon: Server, key: "services" as const, color: "text-primary" },
  { title: "Total Configurations", icon: Settings2, key: "configs" as const, color: "text-info" },
  { title: "Environments", icon: Globe, key: "envs" as const, color: "text-warning" },
  { title: "Latest Updates", icon: Activity, key: "updates" as const, color: "text-destructive" },
];

export default function DashboardPage() {
  const [configs, setConfigs] = useState<Config[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    configApi.getAll().then((data) => {
      setConfigs(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const stats = {
    services: new Set(configs.map((c) => c.service_name)).size,
    configs: configs.length,
    envs: new Set(configs.map((c) => c.environment)).size,
    updates: configs.length > 0 ? configs.length : 0,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Overview of your configuration management system
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => (
          <Card key={card.key} className="bg-card border-border">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.title}
              </CardTitle>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {loading ? "—" : stats[card.key]}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent configs */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-base">Recent Configurations</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading...</p>
          ) : configs.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No configurations yet. Connect your backend at <code className="font-mono text-xs bg-accent px-1.5 py-0.5 rounded">http://localhost:8000</code> and create your first config.
            </p>
          ) : (
            <div className="space-y-2">
              {configs.slice(0, 5).map((c) => (
                <div
                  key={c.id}
                  className="flex items-center justify-between rounded-md bg-accent/50 px-3 py-2 text-sm"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-medium">{c.service_name}</span>
                    <span className="text-xs rounded-full bg-secondary px-2 py-0.5 text-muted-foreground">
                      {c.environment}
                    </span>
                  </div>
                  <span className="font-mono text-xs text-muted-foreground">{c.key}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
