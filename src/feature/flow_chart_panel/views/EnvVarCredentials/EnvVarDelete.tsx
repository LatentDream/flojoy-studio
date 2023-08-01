import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { deleteEnvironmentVariable } from "@src/services/FlowChartServices";
import { useFlowChartState } from "@src/hooks/useFlowChartState";
import { EnvVarCredentialType } from "@src/hooks/useFlowChartState";

export interface EnvVarDeleteProps {
  credential: EnvVarCredentialType;
}

const EnvVarDelete = ({ credential }: EnvVarDeleteProps) => {
  const { setCredentials } = useFlowChartState();

  const handleDelete = (credential: EnvVarCredentialType) => {
    setCredentials((credentials) => {
      return credentials.filter(
        (prevCredential) => prevCredential.id !== credential.id
      );
    });
    deleteEnvironmentVariable({
      key: credential.key,
      value: "",
    });
  };

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild className="h-full w-full border-0">
        <Button variant="outline">Delete</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className="text-black">
            Are you absolutely sure?
          </AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone. This will permanently delete your key
            and remove your data from our servers.
          </AlertDialogDescription>
        </AlertDialogHeader>
        credential
        <AlertDialogFooter>
          <AlertDialogCancel className="text-black">Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={() => handleDelete(credential)}>
            Continue
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default EnvVarDelete;
