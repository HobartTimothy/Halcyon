import { z } from "zod";

export const runEventSchema = z.object({
  schema_version: z.literal("1.0"),
  event_id: z.string().min(1),
  event_type: z.enum([
    "run.started",
    "stage.changed",
    "token.delta",
    "citation.added",
    "approval.required",
    "run.completed",
    "run.failed",
    "stream.snapshot",
    "stream.reset",
  ]),
  run_id: z.string().min(1),
  sequence: z.number().int().nonnegative(),
  data: z.record(z.string(), z.unknown()),
});

export type RunEvent = z.infer<typeof runEventSchema>;

export function parseRunEvent(input: unknown): RunEvent {
  return runEventSchema.parse(input);
}
