import { useEffect, useState } from "react";
import { History } from "lucide-react";
import { configApi } from "@/services/api";
import type { Config } from "@/types/config";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function VersionHistoryPage() {
  const [history, setHistory] = useState<Config[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    configApi.getHistory().then((data) => {
      const sorted = [...data].sort((a, b) => {
        if (a.created_at && b.created_at) return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        return b.version - a.version;
      });
      setHistory(sorted);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Version History</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Track changes across your configurations
        </p>
      </div>

      <div className="rounded-lg border border-border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-secondary/50 hover:bg-secondary/50">
              <TableHead>Service</TableHead>
              <TableHead>Environment</TableHead>
              <TableHead>Key</TableHead>
              <TableHead>Value</TableHead>
              <TableHead>Version</TableHead>
              <TableHead>Timestamp</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : history.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                  No version history found.
                </TableCell>
              </TableRow>
            ) : (
              history.map((h, i) => (
                <TableRow key={`${h.id}-${h.version}-${i}`} className="hover:bg-accent/30">
                  <TableCell className="font-medium">{h.service_name}</TableCell>
                  <TableCell>
                    <span className="text-xs rounded-full bg-secondary px-2 py-0.5">
                      {h.environment}
                    </span>
                  </TableCell>
                  <TableCell className="font-mono text-xs">{h.key}</TableCell>
                  <TableCell className="font-mono text-xs max-w-[200px] truncate">{h.value}</TableCell>
                  <TableCell>{h.version}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {h.created_at ? new Date(h.created_at).toLocaleString() : "—"}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
