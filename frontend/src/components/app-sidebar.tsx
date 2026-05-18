import { NavLink as RouterNavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Settings2,
  FilePlus2,
  History,
  Terminal,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";

const navItems = [
  { title: "Dashboard", to: "/", icon: LayoutDashboard },
  { title: "Configurations", to: "/configs", icon: Settings2 },
  { title: "Create Config", to: "/create-config", icon: FilePlus2 },
  { title: "Version History", to: "/history", icon: History },
];

export function AppSidebar() {
  const { pathname } = useLocation();
  const { user, logout } = useAuth();

  return (
    <aside className="hidden md:flex w-60 flex-col border-r border-border bg-sidebar min-h-screen">
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-5 border-b border-border">
        <div className="flex items-center justify-center h-8 w-8 rounded-md bg-primary">
          <Terminal className="h-4 w-4 text-primary-foreground" />
        </div>
        <span className="font-semibold text-foreground tracking-tight text-lg">CCMS</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const active = pathname === item.to;
          return (
            <RouterNavLink
              key={item.to}
              to={item.to}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                active
                  ? "bg-accent text-foreground"
                  : "text-sidebar-foreground hover:bg-accent hover:text-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.title}
            </RouterNavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-border mt-auto flex flex-col gap-3">
        <div className="flex flex-col">
          <span className="text-sm font-medium text-foreground truncate">
            {user?.username || "Guest"}
          </span>
          <span className="text-xs text-muted-foreground uppercase tracking-wider">
            Role: <span className="font-semibold text-primary">{user?.role || "N/A"}</span>
          </span>
        </div>
        <Button variant="outline" size="sm" onClick={logout} className="w-full justify-start text-muted-foreground hover:text-foreground">
          <LogOut className="h-4 w-4 mr-2" />
          Logout
        </Button>
      </div>
    </aside>
  );
}
