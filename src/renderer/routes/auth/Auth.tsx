import { useAuth } from "@/renderer/context/auth.context";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Separator } from "@/renderer/components/ui/separator";
import { Button } from "@/renderer/components/ui/button";
import { captain } from "@/renderer/lib/ky";
import { User } from "@/types/auth";


type AuthPageProps = {
  startup: boolean;
};

const AuthPage = ({ startup }: AuthPageProps) => {

  const { setUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!startup) setUser(null);
  }, []);

  const handleContinueWithoutSignIn = async () => {
    const user: User = {
      username: "Gui",
      role: "Admin",
      connection: null
    }
    setUser(user);
    await captain.post("auth/login", { json: user });
    navigate("/flowchart");
  }

  const handleSignIn = () => {
    // Set Workspace token
    // Set Permission
    // Set User
    setUser({
      username: "Connected",
      role: "Admin",
      connection: null
    });
  }

  return (
    <>
      <div className="flex h-screen w-screen flex-col items-center justify-center">
        <div className="flex min-w-[600px] min-h-[400px] max-w-5xl gap-4 rounded-md border bg-background p-6 drop-shadow-md">
          <div className="flex flex-col w-1/2 gap-1 pb-3">

            <div className="grow" />
            <h1 className="text-xl font-bold">Sign In</h1>
            <p className="text-xs text-muted-foreground"> Connect with Flojoy to continue</p>
            <Button
              className="w-full h-8 mt-8 text-xs"
              onClick={() => handleSignIn()}
            >Sign In with Flojoy Cloud</Button>
            <div className="flex gap-2 items-center justify-center">
              <Separator className="my-3 w-2/5" />
              <p className="text-xs text-muted-foreground">or</p>
              <Separator className="my-3 w-2/5" />
            </div>
            <Button
              variant="outline"
              className="w-full h-8 text-xs"
              onClick={() => handleContinueWithoutSignIn()}
            >Continue Without Signing In</Button>
            <div className="grow" />

            <div className="flex flex-col h-8">
            </div>

          </div>
          <Separator orientation="vertical" />
          <div className="flex items-center justify-center w-1/2">
            {/* TODO: Replace with Enterprise Logo */}
            <img
              src="/assets/logo.png"
              alt="logo"
              className="h-12 w-12 rounded-full"
            />
          </div>
        </div>
      </div>
    </>
  );
};

export default AuthPage;
