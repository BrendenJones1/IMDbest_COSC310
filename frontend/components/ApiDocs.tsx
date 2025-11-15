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
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl mb-2">API Documentation</h1>
        <p className="text-neutral-400">
          Coming soon...
        </p>
      </div>
    </div>
  );
}