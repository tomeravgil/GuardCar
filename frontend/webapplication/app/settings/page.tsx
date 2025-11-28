"use client";

import { useEffect, useState } from "react";
import Sidebar from "../components/sidebar";

import {
  Card,
  CardHeader,
  CardContent,
  CardTitle,
  CardDescription,
  CardFooter,
} from "../components/ui/card";

import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";
import { Separator } from "../components/ui/separator";
import { toast } from "sonner";

import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "../components/ui/table";


export default function SettingsPage() {
  // ----------------------------
  // FORM STATE (Create Provider)
  // ----------------------------
  const [provider, setProvider] = useState({
    provider_name: "",
    connection_ip: "",
    server_certification: "",
  });

  // ----------------------------
  // SUSPICION CONFIG STATE
  // ----------------------------
  const [suspicionLevel, setSuspicionLevel] = useState("");

  // ----------------------------
  // EXISTING PROVIDERS TABLE
  // ----------------------------
  const [providers, setProviders] = useState<any[]>([]);

  // ----------------------------
  // Load providers on mount
  // ----------------------------
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/providers");
        if (res.ok) {
          const data = await res.json();
          setProviders(data);
        }
      } catch {
        console.warn("Could not load providers.");
      }
    })();
  }, []);

  // ----------------------------
  // SSE LISTENER
  // ----------------------------
  useEffect(() => {
    const sse = new EventSource("http://127.0.0.1:8000/api/sse");

    sse.onopen = () => console.log("[SSE] Connection opened.");
    sse.onerror = (e) => console.log("[SSE] Connection error:", e);

    sse.addEventListener("success", (e: any) => {
      try {
        const data = JSON.parse(e.data);
        if (data.related_to === "cloud") {
          toast.success(data.message);
          // Refresh providers list
          fetch("http://127.0.0.1:8000/api/providers")
            .then((r) => r.json())
            .then(setProviders);
        } else if (data.related_to === "suspicion") {
          toast.success(data.message);
        }
      } catch (err) {
        console.error("SSE Parse Error", err);
      }
    });

    sse.addEventListener("failure", (e: any) => {
      try {
        const data = JSON.parse(e.data);
        if (data.related_to === "cloud") {
          toast.error(data.message);
        } else if (data.related_to === "suspicion") {
          toast.error(data.message);
        }
      } catch (err) {
        console.error("SSE Parse Error", err);
      }
    });

    return () => {
      sse.close();
    };
  }, []);

  // ----------------------------
  // INPUT HANDLERS
  // ----------------------------
  const handleProviderChange = (e: any) => {
    const { name, value } = e.target;
    setProvider((prev) => ({ ...prev, [name]: value }));
  };

  // ----------------------------
  // REGISTER PROVIDER
  // ----------------------------
  const createProvider = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/register_provider", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(provider),
      });

      if (!res.ok) throw new Error();

      toast.info("Request sent. Waiting for confirmation...");

      // clear form
      setProvider({
        provider_name: "",
        connection_ip: "",
        server_certification: "",
      });
    } catch {
      toast.error("Failed to send registration request.");
    }
  };

  // ----------------------------
  // DELETE PROVIDER
  // ----------------------------
  const deleteProvider = async (provider_name: string) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/delete_provider", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider_name }),
      });

      if (!res.ok) throw new Error();

      toast.info("Request sent. Waiting for confirmation...");
    } catch {
      toast.error("Failed to send delete request.");
    }
  };

  // ----------------------------
  // UPDATE SUSPICION LEVEL
  // ----------------------------
  const updateSuspicionLevel = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/suspicion_config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          suspicion_level: Number(suspicionLevel),
        }),
      });

      if (!res.ok) throw new Error();

      toast.info("Request sent. Waiting for confirmation...");
    } catch {
      toast.error("Failed to send update request.");
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <main className="flex-1 p-10">
        <h1 className="text-3xl font-bold mb-8 text-gray-800">Settings</h1>

        <div className="space-y-10">
          {/* ---------------------------- */}
          {/* CLOUD PROVIDERS SECTION      */}
          {/* ---------------------------- */}
          <Card>
            <CardHeader>
              <CardTitle>Cloud Providers</CardTitle>
              <CardDescription>
                Add or remove cloud inference providers.
              </CardDescription>
            </CardHeader>

            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex flex-col space-y-2">
                <Label>Provider Name</Label>
                <Input
                  name="provider_name"
                  value={provider.provider_name}
                  onChange={handleProviderChange}
                />
              </div>

              <div className="flex flex-col space-y-2">
                <Label>Connection IP</Label>
                <Input
                  name="connection_ip"
                  value={provider.connection_ip}
                  onChange={handleProviderChange}
                />
              </div>

              <div className="flex flex-col space-y-2 md:col-span-2">
                <Label>Server Certification</Label>
                <Input
                  name="server_certification"
                  value={provider.server_certification}
                  onChange={handleProviderChange}
                />
              </div>
            </CardContent>

            <CardFooter>
              <Button onClick={createProvider}>Register Provider</Button>
            </CardFooter>
          </Card>

          {/* PROVIDERS TABLE */}
          <Card>
            <CardHeader>
              <CardTitle>Registered Providers</CardTitle>
              <CardDescription>Manage existing providers.</CardDescription>
            </CardHeader>

            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Provider Name</TableHead>
                    <TableHead>Connection IP</TableHead>
                    <TableHead>Server Cert</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>

                <TableBody>
                  {providers.map((p) => (
                    <TableRow key={p.provider_name}>
                      <TableCell>{p.provider_name}</TableCell>
                      <TableCell>{p.connection_ip}</TableCell>
                      <TableCell className="max-w-[200px] truncate">
                        {p.server_certification}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => deleteProvider(p.provider_name)}
                        >
                          Delete
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}

                  {providers.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center text-gray-500">
                        No providers registered.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <Separator />

          {/* ---------------------------- */}
          {/* SUSPICION CONFIG SECTION     */}
          {/* ---------------------------- */}
          <Card>
            <CardHeader>
              <CardTitle>Suspicion Configuration</CardTitle>
              <CardDescription>
                Set the global suspicion threshold level.
              </CardDescription>
            </CardHeader>

            <CardContent className="flex flex-col space-y-4">
              <Label>Suspicion Level</Label>
              <Input
                type="number"
                min="0"
                max="100"
                value={suspicionLevel}
                onChange={(e) => setSuspicionLevel(e.target.value)}
              />
            </CardContent>

            <CardFooter>
              <Button onClick={updateSuspicionLevel}>Save Level</Button>
            </CardFooter>
          </Card>
        </div>
      </main>
    </div>
  );
}
