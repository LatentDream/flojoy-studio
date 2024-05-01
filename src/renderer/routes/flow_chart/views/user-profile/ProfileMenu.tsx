import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/renderer/components/ui/dropdown-menu";
import { Fragment, useState } from "react";
import { useAuth } from "@/renderer/context/auth.context";
import { useNavigate } from "react-router-dom";
import { Badge } from "@/renderer/components/ui/badge";
import { Button } from "@/renderer/components/ui/button";

const ProfileMenu = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const handleSwitchUser = () => {
    navigate(`/auth/user-switch`);
  };
  if (!user || user.connection === null) {
    return <Button  onClick={handleSwitchUser}>Sign In</Button>
  }
  return (
    <Fragment>
      <DropdownMenu>
        <DropdownMenuTrigger className="flex items-center gap-2 px-2">
          {user.username.slice(0, 10)}
          <Badge> {user.role} </Badge>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="mt-2">
          <DropdownMenuLabel>{user.role}</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => handleSwitchUser()}>
            Switch user profile
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </Fragment>
  );
};

export default ProfileMenu;
