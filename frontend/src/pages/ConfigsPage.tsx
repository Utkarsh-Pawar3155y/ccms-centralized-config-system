import { useEffect, useState } from "react";
import { configApi } from "@/services/api";
import type { Config } from "@/types/config";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Pencil, Trash2, Search } from "lucide-react";
import { toast } from "sonner";
import { Label } from "@/components/ui/label";

export default function ConfigsPage() {
  const [configs, setConfigs] = useState<Config[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  // Edit modal
  const [editOpen, setEditOpen] = useState(false);
  const [editConfig, setEditConfig] = useState<Config | null>(null);
  const [editValue, setEditValue] = useState("");

  // Delete dialog
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const fetchConfigs = () => {
    setLoading(true);
    configApi.getAll().then((data) => {
      setConfigs(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => { fetchConfigs(); }, []);

  const filtered = configs.filter((c) => {
    const q = search.toLowerCase();
    return (
      (c.service_name || "").toLowerCase().includes(q) ||
      (c.environment || "").toLowerCase().includes(q) ||
      (c.key || "").toLowerCase().includes(q)
    );
  });

  const handleEdit = (config: Config) => {
    setEditConfig(config);
    setEditValue(config.value);
    setEditOpen(true);
  };

  const submitEdit = async () => {
    if (!editConfig) return;
    try {
      await configApi.update(editConfig.id, { value: editValue });
      toast.success("Configuration updated");
      setEditOpen(false);
      fetchConfigs();
    } catch {
      toast.error("Failed to update configuration");
    }
  };

  const handleDelete = (id: string) => {
    setDeleteId(id);
    setDeleteOpen(true);
  };

  const confirmDelete = async () => {
    if (!deleteId) return;
    try {
      await configApi.delete(deleteId);
      toast.success("Configuration deleted");
      setDeleteOpen(false);
      fetchConfigs();
    } catch {
      toast.error("Failed to delete configuration");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Configurations</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Manage all your service configurations
        </p>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search configs..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9 bg-secondary border-border"
        />
      </div>

      {/* Table */}
      <div className="rounded-lg border border-border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-secondary/50 hover:bg-secondary/50">
              <TableHead>Service</TableHead>
              <TableHead>Environment</TableHead>
              <TableHead>Key</TableHead>
              <TableHead>Value</TableHead>
              <TableHead>Version</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                  Loading...
                </TableCell>
              </TableRow>
            ) : filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                  No configurations found. Make sure your backend is running.
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((c) => (
                <TableRow key={c.id} className="hover:bg-accent/30">
                  <TableCell className="font-medium">{c.service_name}</TableCell>
                  <TableCell>
                    <span className="text-xs rounded-full bg-secondary px-2 py-0.5">
                      {c.environment}
                    </span>
                  </TableCell>
                  <TableCell className="font-mono text-xs">{c.key}</TableCell>
                  <TableCell className="font-mono text-xs max-w-[200px] truncate">
                    {c.value}
                  </TableCell>
                  <TableCell>{c.version}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Button variant="ghost" size="icon" onClick={() => handleEdit(c)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(c.id)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="bg-card border-border">
          <DialogHeader>
            <DialogTitle>Edit Configuration</DialogTitle>
          </DialogHeader>
          {editConfig && (
            <div className="space-y-4 py-2">
              <div className="text-sm space-y-1">
                <p><span className="text-muted-foreground">Service:</span> {editConfig.service_name}</p>
                <p><span className="text-muted-foreground">Environment:</span> {editConfig.environment}</p>
                <p><span className="text-muted-foreground">Key:</span> <code className="font-mono text-xs">{editConfig.key}</code></p>
              </div>
              <div className="space-y-2">
                <Label>Value</Label>
                <Input
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="bg-secondary border-border"
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)}>Cancel</Button>
            <Button onClick={submitEdit}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirm */}
      <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <AlertDialogContent className="bg-card border-border">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Configuration</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. The configuration will be permanently removed.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
