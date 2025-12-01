import { Code, Copy, Check } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { useState } from "react";
import { Button } from "./ui/button";

interface CodeBlockProps {
  code: string;
  language?: string;
}

function CodeBlock({ code, language = "json" }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="icon"
        className="absolute top-2 right-2 h-8 w-8 text-neutral-400 hover:text-white"
        onClick={handleCopy}
      >
        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
      </Button>
      <pre className="bg-neutral-950 border border-neutral-800 rounded-lg p-4 overflow-x-auto">
        <code className="text-sm text-neutral-300">{code}</code>
      </pre>
    </div>
  );
}

interface EndpointProps {
  method: string;
  path: string;
  description: string;
  request?: string;
  response: string;
  params?: { name: string; type: string; description: string }[];
}

function Endpoint({ method, path, description, request, response, params }: EndpointProps) {
  const methodColors: Record<string, string> = {
    GET: "bg-green-600",
    POST: "bg-blue-600",
    PUT: "bg-yellow-600",
    DELETE: "bg-red-600",
  };

  return (
    <Card className="bg-neutral-900 border-neutral-800">
      <CardHeader>
        <div className="flex items-center gap-3 mb-2">
          <Badge className={`${methodColors[method]} text-white`}>{method}</Badge>
          <code className="text-sm bg-neutral-950 px-3 py-1 rounded border border-neutral-800">
            {path}
          </code>
        </div>
        <CardDescription className="text-neutral-300">{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {params && params.length > 0 && (
          <div>
            <h4 className="mb-2">Parameters</h4>
            <div className="space-y-2">
              {params.map((param) => (
                <div key={param.name} className="flex gap-2">
                  <code className="bg-neutral-950 px-2 py-1 rounded text-sm">
                    {param.name}
                  </code>
                  <Badge variant="outline" className="border-neutral-700">
                    {param.type}
                  </Badge>
                  <span className="text-sm text-neutral-400">{param.description}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {request && (
          <div>
            <h4 className="mb-2">Request Body</h4>
            <CodeBlock code={request} />
          </div>
        )}

        <div>
          <h4 className="mb-2">Response</h4>
          <CodeBlock code={response} />
        </div>
      </CardContent>
    </Card>
  );
}

export function ApiDocs() {
  const searchEndpoints: EndpointProps[] = [
    {
      method: "GET",
      path: "/search",
      description: "Search the movie catalog with optional sorting and pagination.",
      params: [
        { name: "q", type: "string", description: "Search term (default empty string)." },
        { name: "limit", type: "number", description: "Results per page (default 20)." },
        { name: "sort_by", type: "title|rating|year", description: "Sort key." },
        { name: "sort_order", type: "asc|desc", description: "Sort direction (default asc)." },
      ],
      response: `{
  "items": [
    {
      "id": "tt0944947",
      "title": "Game of Thrones",
      "year": 2011
    }
  ],
  "total": 1
}`,
    },
  ];

  const userEndpoints: EndpointProps[] = [
    {
      method: "POST",
      path: "/users/register",
      description: "Create a new account and receive an auth token.",
      request: `{
  "username": "sam",
  "email": "sam@example.com",
  "password": "supersecret"
}`,
      response: `{
  "token": "<jwt>",
  "user": {
    "id": "c5ab...",
    "username": "sam",
    "email": "sam@example.com",
    "registered_at": "2024-03-01T18:21:00+00:00"
  }
}`,
    },
    {
      method: "POST",
      path: "/users/login",
      description: "Authenticate with username + password. Returns a token + user.",
      params: [
        { name: "username", type: "string", description: "Username (case-insensitive)." },
        { name: "password", type: "string", description: "Plain-text password." },
      ],
      response: `{
  "token": "<jwt>",
  "user": {
    "id": "c5ab...",
    "username": "sam",
    "email": "sam@example.com"
  }
}`,
    },
    {
      method: "GET",
      path: "/users/",
      description: "List all users (public-safe payload).",
      response: `[
  {
    "id": "c5ab...",
    "username": "sam",
    "email": "sam@example.com"
  }
]`,
    },
    {
      method: "GET",
      path: "/users/{id}",
      description: "Fetch a single user by id.",
      response: `{
  "id": "c5ab...",
  "username": "sam",
  "email": "sam@example.com",
  "watchlist": []
}`,
    },
  ];

  const flagEndpoints: EndpointProps[] = [
    {
      method: "POST",
      path: "/flags",
      description: "Report a review/user for moderation.",
      request: `{
  "review_id": 5,
  "flagger_id": 12,
  "flagged_user_id": 8,
  "reason": "abusive"
}`,
      response: `{
  "flag_id": 1,
  "review_id": 5,
  "flagger_id": 12,
  "flagged_user_id": 8,
  "reason": "abusive",
  "status": "pending",
  "date_created": "2025-10-27T23:51:13.300022"
}`,
    },
    {
      method: "GET",
      path: "/flags",
      description: "List all flags (optional ?status=pending|approved|rejected).",
      response: `[
  {
    "flag_id": 1,
    "status": "pending"
  }
]`,
    },
    {
      method: "PATCH",
      path: "/flags/{flag_id}/status",
      description: "Update moderation status for a flag.",
      request: `{
  "status": "approved"
}`,
      response: `{
  "flag_id": 1,
  "status": "approved"
}`,
    },
  ];

  const penaltyEndpoints: EndpointProps[] = [
    {
      method: "POST",
      path: "/penalties",
      description: "Issue a penalty referencing a flag or direct moderation action.",
      request: `{
  "user_id": 8,
  "issued_by": 99,
  "reason": "abusive",
  "source_flag_id": 55
}`,
      response: `{
  "penalty_id": 1,
  "user_id": 8,
  "reason": "abusive",
  "active": true,
  "date_created": "2025-10-27T23:51:13.300022"
}`,
    },
    {
      method: "GET",
      path: "/penalties",
      description: "List penalties (optional ?user_id= to filter).",
      response: `[
  {
    "penalty_id": 1,
    "user_id": 8,
    "reason": "abusive",
    "active": true
  }
]`,
    },
    {
      method: "POST",
      path: "/penalties/{penalty_id}/deactivate",
      description: "Deactivate an active penalty.",
      request: `{
  "revoked_by": 101
}`,
      response: `{
  "penalty_id": 1,
  "active": false
}`,
    },
  ];

  const adminEndpoints: EndpointProps[] = [
    {
      method: "GET",
      path: "/admin/users",
      description: "Admin-only: list all users with sensitive fields.",
      response: `[
  {
    "id": "c5ab...",
    "username": "sam",
    "email": "sam@example.com",
    "penalties": []
  }
]`,
    },
    {
      method: "DELETE",
      path: "/admin/users/{user_id}",
      description: "Delete a user and their associated data (requires admin JWT).",
      response: `{
  "detail": "User deleted"
}`,
    },
    {
      method: "POST",
      path: "/admin/users/{user_id}/promote",
      description: "Promote a user to admin.",
      response: `{
  "detail": "User promoted"
}`,
    },
    {
      method: "GET",
      path: "/admin/users/{user_id}/reviews",
      description: "List all reviews written by a user.",
      response: `[
  {
    "movie_id": "tt123",
    "rating": 9,
    "comment": "Fantastic!"
  }
]`,
    },
    {
      method: "DELETE",
      path: "/admin/users/{user_id}/reviews/delete",
      description: "Delete a specific review (?movie_id=).",
      params: [{ name: "movie_id", type: "string", description: "Review identifier to delete." }],
      response: `{
  "detail": "Review deleted"
}`,
    },
    {
      method: "GET",
      path: "/admin/users/{user_id}/penalties",
      description: "Fetch all penalties for a user.",
      response: `[
  {
    "penalty_id": 1,
    "reason": "spam"
  }
]`,
    },
    {
      method: "POST",
      path: "/admin/users/{user_id}/penalties",
      description: "Issue a penalty via admin panel (?reason=&flag_id=).",
      params: [
        { name: "reason", type: "string", description: "Moderator facing note." },
        { name: "flag_id", type: "number?", description: "Optional flag reference." },
      ],
      response: `{
  "penalty_id": 22,
  "reason": "spam"
}`,
    },
    {
      method: "PUT",
      path: "/admin/penalties/{penalty_id}/deactivate",
      description: "Deactivate a penalty via admin panel.",
      response: `{
  "penalty_id": 22,
  "active": false
}`,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl mb-2">API Documentation</h1>
        <p className="text-neutral-400">
          Base URL: <code className="text-white">http://localhost:8000</code>. All JSON responses are UTF-8 and most endpoints are stateless. JWT-protected routes require an <code>Authorization: Bearer &lt;token&gt;</code> header.
        </p>
      </div>

      <Tabs defaultValue="search" className="space-y-6">
        <TabsList className="bg-neutral-900 border-neutral-800">
          <TabsTrigger value="search">Search</TabsTrigger>
          <TabsTrigger value="users">Users & Auth</TabsTrigger>
          <TabsTrigger value="flags">Flags</TabsTrigger>
          <TabsTrigger value="penalties">Penalties</TabsTrigger>
          <TabsTrigger value="admin">Admin</TabsTrigger>
        </TabsList>

        <TabsContent value="search" className="space-y-4">
          {searchEndpoints.map((endpoint) => (
            <Endpoint key={endpoint.path} {...endpoint} />
          ))}
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          {userEndpoints.map((endpoint) => (
            <Endpoint key={endpoint.path} {...endpoint} />
          ))}
        </TabsContent>

        <TabsContent value="flags" className="space-y-4">
          {flagEndpoints.map((endpoint) => (
            <Endpoint key={endpoint.path} {...endpoint} />
          ))}
        </TabsContent>

        <TabsContent value="penalties" className="space-y-4">
          {penaltyEndpoints.map((endpoint) => (
            <Endpoint key={endpoint.path} {...endpoint} />
          ))}
        </TabsContent>

        <TabsContent value="admin" className="space-y-4">
          <Card className="bg-neutral-900 border-neutral-800">
            <CardHeader>
              <CardTitle>Authentication</CardTitle>
              <CardDescription className="text-neutral-300">
                All <code className="text-white">/admin/*</code> routes require a JWT with role <code className="text-white">admin</code>.
              </CardDescription>
            </CardHeader>
          </Card>
          {adminEndpoints.map((endpoint) => (
            <Endpoint key={endpoint.path + endpoint.method} {...endpoint} />
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}
