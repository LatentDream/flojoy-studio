export const allRoles = ["Admin", "Operator", "Local"] as const;
export type Role = (typeof allRoles)[number];

export type User = {
  role: Role;
  // Field for if connected to a workspace
  name: string;
  token?: string;
  workspace?: string;
  logged?: boolean;
};
