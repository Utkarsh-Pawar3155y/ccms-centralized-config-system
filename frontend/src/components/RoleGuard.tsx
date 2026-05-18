import { ReactNode } from "react";
import { useAuth } from "@/context/AuthContext";

interface RoleGuardProps {
  allowedRoles: string[];
  children: ReactNode;
}

export function RoleGuard({ allowedRoles, children }: RoleGuardProps) {
  const { role } = useAuth();

  if (!role || !allowedRoles.includes(role)) {
    return null;
  }

  return <>{children}</>;
}
