import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";

export function ApiDocs() {
  return (
    <div className="space-y-6">
      <Card className="bg-neutral-900 border-neutral-800">
        <CardHeader>
          <CardTitle>API Documentation</CardTitle>
          <CardDescription className="text-neutral-400">
            Real API docs are on the way. For now, you can explore the backend endpoints
            at <code>/auth</code>, <code>/search</code>, and the watchlist routes.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-neutral-300 text-sm">
          <p>
            Use the new authentication endpoints (<code>/auth/register</code>, <code>/auth/login</code>,
            <code>/auth/me</code>) to obtain a JWT token. Include that token in the
            <code>Authorization</code> header as <code>Bearer &lt;token&gt;</code> when calling protected routes.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
