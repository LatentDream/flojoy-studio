import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { User } from "src/types/auth";

type States = {
  user: User | null;
  setUser: (user: User | null) => void;
  users: User[];
  refreshUsers: () => void;
  isConnected: boolean;
};

export const AuthContext = createContext<States>({
  refreshUsers: () => {},
  user: null,
  users: [],
  setUser: () => {},
  isConnected: false,
});

export const AuthContextProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);

  const refreshUsers = useCallback(async () => {
    setUsers([]);
  }, []);

  useEffect(() => {
    refreshUsers();
  }, [refreshUsers]);

  const values = useMemo(
    () => ({
      user,
      setUser,
      users,
      refreshUsers,
      isConnected : user !== null && user.connection !== null
    }),
    [user, users, refreshUsers],
  );

  return <AuthContext.Provider value={values}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within a AuthProvider");
  }
  return ctx;
};
