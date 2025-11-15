import { Home, Heart, Settings, BookOpen, Film } from "lucide-react";
import { Button } from "./ui/button";

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export function Sidebar({ activeSection, onSectionChange, onAccessAdmin }: SidebarProps & { onAccessAdmin?: () => boolean }) {
  const menuItems = [
    { id: "home", label: "Dashboard", icon: Home },
    { id: "watchlist", label: "Watchlist", icon: Heart },
    { id: "admin", label: "Admin", icon: Settings },
    { id: "docs", label: "Docs", icon: BookOpen },
  ];

  const visibleMenuItems = menuItems.filter((item) => {
    if (item.id === "admin" && typeof onAccessAdmin === "function") {
      return onAccessAdmin();
    }
    return true;
  });

  return (
    <div className="w-56 bg-neutral-900 border-r border-neutral-800 flex flex-col py-6 gap-6">
      <div className="px-6 mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-red-800 rounded-lg flex items-center justify-center">
            <Film className="h-5 w-5 text-white" />
          </div>
          <span className="tracking-tight">IMDB</span>
        </div>
      </div>

      <div className="flex flex-col gap-1 flex-1 px-3">
        {visibleMenuItems.map((item) => {
          const Icon = item.icon;
          return (
            <Button
              key={item.id}
              variant={activeSection === item.id ? "secondary" : "ghost"}
              className={`w-full justify-start gap-3 h-11 px-3 rounded-lg ${
                activeSection === item.id ? "bg-neutral-800 text-white" : "text-neutral-400 hover:text-white hover:bg-neutral-800/50"
              }`}
              onClick={() => onSectionChange(item.id)}
            >
              <Icon className="h-5 w-5" />
              <span>{item.label}</span>
            </Button>
          );
        })}
      </div>
    </div>
  );
}
