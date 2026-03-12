import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { configApi } from "@/services/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

const environments = ["dev", "staging", "prod"];

export default function CreateConfigPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    service: "",
    environment: "",
    key: "",
    value: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.service || !form.environment || !form.key || !form.value) {
      toast.error("All fields are required");
      return;
    }
    setLoading(true);
    try {
      await configApi.create({
        service_name: form.service,
        environment: form.environment,
        key: form.key,
        value: form.value,
      });
      toast.success("Configuration created successfully");
      navigate("/configs");
    } catch {
      toast.error("Failed to create configuration");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Create Configuration</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Add a new configuration entry for a service
        </p>
      </div>

      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-base">New Config</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Service Name</Label>
              <Input
                placeholder="e.g. user-service"
                value={form.service}
                onChange={(e) => setForm({ ...form, service: e.target.value })}
                className="bg-secondary border-border"
              />
            </div>

            <div className="space-y-2">
              <Label>Environment</Label>
              <Select
                value={form.environment}
                onValueChange={(val) => setForm({ ...form, environment: val })}
              >
                <SelectTrigger className="bg-secondary border-border">
                  <SelectValue placeholder="Select environment" />
                </SelectTrigger>
                <SelectContent>
                  {environments.map((env) => (
                    <SelectItem key={env} value={env}>
                      {env}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Key</Label>
              <Input
                placeholder="e.g. DATABASE_URL"
                value={form.key}
                onChange={(e) => setForm({ ...form, key: e.target.value })}
                className="bg-secondary border-border font-mono text-sm"
              />
            </div>

            <div className="space-y-2">
              <Label>Value</Label>
              <Input
                placeholder="e.g. postgres://..."
                value={form.value}
                onChange={(e) => setForm({ ...form, value: e.target.value })}
                className="bg-secondary border-border font-mono text-sm"
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creating..." : "Create Configuration"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
