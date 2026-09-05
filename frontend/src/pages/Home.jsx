import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function Home() {
  const { data } = useQuery({
    queryKey: ["health"],
    queryFn: () => api("/health"),
  });

  return (
    <main className="p-6">
      <h1 className="text-2xl font-semibold">Welcome to GigBridge</h1>
      <p className="text-gray-600 mt-2">
        Backend status: {data ? data.status : "connecting..."}
      </p>
    </main>
  );
}
