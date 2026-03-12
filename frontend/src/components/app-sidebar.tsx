import { NavLink as RouterNavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Settings2,
  FilePlus2,
  History,
  Terminal,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { title: "Dashboard", to: "/", icon: LayoutDashboard },
  { title: "Configurations", to: "/configs", icon: Settings2 },
  { title: "Create Config", to: "/create-config", icon: FilePlus2 },
  { title: "Version History", to: "/history", icon: History },
];

export function AppSidebar() {
  const { pathname } = useLocation();

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
      <div className="px-5 py-4 border-t border-border">
        <p className="text-xs text-muted-foreground">CCMS v1.0</p>
      </div>
    </aside>
  );
}
