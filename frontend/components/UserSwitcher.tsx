import { User, ChevronDown, LogOut, Settings } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Button } from "./ui/button";

interface UserSwitcherProps {
  currentUser: string;
  currentUserEmail?: string;
  onSignOut?: () => void;
}

export function UserSwitcher({ currentUser, currentUserEmail, onSignOut }: UserSwitcherProps) {
  const handleSignOut = () => {
    if (onSignOut) {
      onSignOut();
    } else {
      // Default demo behavior - show alert
      alert("Sign out clicked - In production, this would sign out the user");
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="gap-2 bg-neutral-800 border-neutral-700 text-white hover:bg-neutral-700">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center">
            <User className="h-4 w-4 text-white" />
          </div>
          <span>{currentUser}</span>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="bg-neutral-800 border-neutral-700 text-white w-56">
        <DropdownMenuLabel>
          <div className="flex flex-col">
            <span>{currentUser}</span>
            {currentUserEmail && (
              <span className="text-xs text-neutral-400">{currentUserEmail}</span>
            )}
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-neutral-700" />
        <DropdownMenuItem
          onClick={handleSignOut}
          className="hover:bg-neutral-700 cursor-pointer text-red-400 focus:text-red-400"
        >
          <LogOut className="h-4 w-4 mr-2" />
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
