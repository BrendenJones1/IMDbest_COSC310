import { User as UserIcon, Mail, Calendar, Heart, MessageSquare } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

interface User {
  id: string;
  name: string;
  email: string;
  joinDate: string;
  watchlistCount: number;
  reviewCount: number;
}

interface UserManagementProps {
  users: User[];
  currentUser: string;
  onUserChange: (userId: string) => void;
}

export function UserManagement({ users, currentUser, onUserChange }: UserManagementProps) {
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase();
  };

  const getAvatarColor = (userId: string) => {
    const colors = [
      "from-purple-600 to-pink-600",
      "from-blue-600 to-cyan-600",
      "from-green-600 to-emerald-600",
    ];
    const index = users.findIndex((u) => u.id === userId);
    return colors[index % colors.length];
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl mb-2">User Management</h1>
          <p className="text-neutral-400">
            Switch between users or view user statistics
          </p>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="bg-neutral-900 border-neutral-800">
              Switch User
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-neutral-900 border-neutral-800">
            {users.map((user) => (
              <DropdownMenuItem
                key={user.id}
                onClick={() => onUserChange(user.id)}
                className="cursor-pointer"
              >
                {user.name}
                {currentUser === user.id && (
                  <Badge className="ml-2 bg-green-600">Active</Badge>
                )}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {users.map((user) => (
          <Card
            key={user.id}
            className={`bg-neutral-900 border-2 transition-all cursor-pointer hover:border-neutral-600 ${
              currentUser === user.id
                ? "border-purple-600"
                : "border-neutral-800"
            }`}
            onClick={() => onUserChange(user.id)}
          >
            <CardHeader>
              <div className="flex items-center gap-4">
                <Avatar className="h-16 w-16">
                  <AvatarFallback
                    className={`bg-gradient-to-br ${getAvatarColor(user.id)} text-white`}
                  >
                    {getInitials(user.name)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <CardTitle>{user.name}</CardTitle>
                    {currentUser === user.id && (
                      <Badge className="bg-purple-600">Active</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-1 text-sm text-neutral-400 mt-1">
                    <Mail className="h-3 w-3" />
                    <span>{user.email}</span>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-neutral-400">
                <Calendar className="h-4 w-4" />
                <span>Joined {user.joinDate}</span>
              </div>
              <div className="grid grid-cols-2 gap-3 pt-3 border-t border-neutral-800">
                <div className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-full bg-red-600/20 flex items-center justify-center">
                    <Heart className="h-4 w-4 text-red-400" />
                  </div>
                  <div>
                    <div className="text-sm text-neutral-400">Watchlist</div>
                    <div>{user.watchlistCount}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-8 w-8 rounded-full bg-blue-600/20 flex items-center justify-center">
                    <MessageSquare className="h-4 w-4 text-blue-400" />
                  </div>
                  <div>
                    <div className="text-sm text-neutral-400">Reviews</div>
                    <div>{user.reviewCount}</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-neutral-900 border-neutral-800">
        <CardHeader>
          <CardTitle>Current Active User</CardTitle>
        </CardHeader>
        <CardContent>
          {users.map(
            (user) =>
              currentUser === user.id && (
                <div key={user.id} className="flex items-center gap-4">
                  <Avatar className="h-20 w-20">
                    <AvatarFallback
                      className={`bg-gradient-to-br ${getAvatarColor(user.id)} text-white text-xl`}
                    >
                      {getInitials(user.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <h3 className="text-xl mb-1">{user.name}</h3>
                    <div className="flex items-center gap-4 text-sm text-neutral-400">
                      <div className="flex items-center gap-1">
                        <Mail className="h-4 w-4" />
                        <span>{user.email}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>Joined {user.joinDate}</span>
                      </div>
                    </div>
                    <div className="flex gap-4 mt-3">
                      <div className="flex items-center gap-2 bg-neutral-800 px-3 py-2 rounded-lg">
                        <Heart className="h-4 w-4 text-red-400" />
                        <span className="text-sm">
                          {user.watchlistCount} movies in watchlist
                        </span>
                      </div>
                      <div className="flex items-center gap-2 bg-neutral-800 px-3 py-2 rounded-lg">
                        <MessageSquare className="h-4 w-4 text-blue-400" />
                        <span className="text-sm">{user.reviewCount} reviews</span>
                      </div>
                    </div>
                  </div>
                </div>
              )
          )}
        </CardContent>
      </Card>
    </div>
  );
}
