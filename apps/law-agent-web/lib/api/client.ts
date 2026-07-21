import { z } from "zod";

const demoRunResponseSchema = z.object({
  run_id: z.string().min(1),
  final_answer: z.string(),
  evidence_count: z.number().int().nonnegative(),
});

export type DemoRunResponse = z.infer<typeof demoRunResponseSchema>;

export async function executeDemoRun(query: string): Promise<DemoRunResponse> {
  const response = await fetch("/api/v1/runs/demo", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!response.ok) {
    throw new Error(`Run request failed with status ${response.status}`);
  }
  return demoRunResponseSchema.parse(await response.json());
}
