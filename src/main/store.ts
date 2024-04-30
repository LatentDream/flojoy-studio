import Store from "electron-store";
import os from "os";
import { User } from "../types/auth";

type TypedStore = {
  poetryOptionalGroups: string[];
  users: User[];
};

export const store = new Store<TypedStore>({
  defaults: {
    poetryOptionalGroups: [],
    users: [
      {
        username: os.userInfo().username,
        role: "Local",
        logged: true,
      },
    ],
  },
});
