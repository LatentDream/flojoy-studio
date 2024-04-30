import * as z from "zod";

export const allRoles = z.enum(["Admin", "Operator"]);
export type Role = z.infer<typeof allRoles>;

const CloudConnection = z.object({
  token: z.string(),
  workspace: z.string(),
  cloudUrl: z.string(),
});
type CloudConnection = z.infer<typeof CloudConnection>;

const User = z.object({
  username: z.string(),
  role: allRoles,
  connection: CloudConnection.nullable(),
});
export type User = z.infer<typeof User>;
