import { useEffect, useState } from "react";
import { Input } from "@/renderer/components/ui/input";
import { useTestSequencerState } from "@/renderer/hooks/useTestSequencerState";
import LockableButton from "./lockable/LockedButtons";
import { useTestSequencerWS } from "@/renderer/context/testSequencerWS.context";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/renderer/components/ui/select";
import { Button } from "@/renderer/components/ui/button";
import { useAppStore } from "@/renderer/stores/app";
import { useShallow } from "zustand/react/shallow";
import { testSequenceExportCloud } from "@/renderer/routes/test_sequencer_panel/models/models";
import { getCloudProjects, getEnvironmentVariables } from "@/renderer/lib/api";
import { toastQueryError } from "@/renderer/utils/report-error";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Spinner } from "@/renderer/components/ui/spinner";
import { ControlButton } from "./ControlButton";
import { TestSequenceContainer } from "@/renderer/types/test-sequencer";
import { Badge } from "@/renderer/components/ui/badge";

const getIntegrity = (sequences: TestSequenceContainer[]): boolean => {
  let integrity = true;
  sequences.forEach((seq) => {
    integrity = integrity && seq.runable;
  });
  return integrity;
}


export function CloudPanel() {
  const queryClient = useQueryClient();
  const [serialNumber, setSerialNumber] = useState("");
  const [lotNumber, setLotNumber] = useState("");
  const [projectId, setProjectId] = useState("");
  const [partNumber, setPartNumber] = useState("");
  const { tree, setIsLocked, isLocked, sequences } = useTestSequencerState();
  const { tSSendJsonMessage } = useTestSequencerWS();

  const envsQuery = useQuery({
    queryKey: ["envs"],
    queryFn: async () => {
      const res = await getEnvironmentVariables();
      return res.match(
        (vars) => vars,
        (e) => {
          toastQueryError(e, "Failed to fetch environment variables");
          return [];
        },
      );
    },
  });

  const projectsQuery = useQuery({
    queryKey: ["projects"],
    queryFn: async () => {
      if (envsQuery.isSuccess) {
        if (
          envsQuery.data.some((c) => c.key === "FLOJOY_CLOUD_WORKSPACE_SECRET")
        ) {
          const res = await getCloudProjects();
          return res.match(
            (vars) => vars,
            (e) => {
              toastQueryError(e, "Failed to fetch cloud projects");
              return [];
            },
          );
        }
      }
      return [];
    },
    enabled: envsQuery.isSuccess,
  });

  // Todo: part query base on the project id
  const dummyPartQuery = ["part1", "part2", "part3"];

  const { isEnvVarModalOpen, setIsEnvVarModalOpen } = useAppStore(
    useShallow((state) => ({
      isEnvVarModalOpen: state.isEnvVarModalOpen,
      setIsEnvVarModalOpen: state.setIsEnvVarModalOpen,
    })),
  );

  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ["envs"] });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isEnvVarModalOpen]);

  const handleExport = () => {
    tSSendJsonMessage(testSequenceExportCloud(tree, serialNumber, projectId));
    setIsLocked(true);
  };

  if (!envsQuery.isSuccess || !projectsQuery.isSuccess) {
    return (
      <div className="grid grid-cols-1 gap-4 place-items-center pt-5">
        <Spinner />
      </div>
    );
  }

  const isCloudKeySet = envsQuery.data.some(
    (c) => c.key === "FLOJOY_CLOUD_WORKSPACE_SECRET",
  );


  return (
    <div className="mt-5 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 rounded-lg border bg-card text-card-foreground shadow-sm p-6 ml-5">
      <h3 className="text-2xl font-semibold leading-none tracking-tight">Report</h3>
      <p className="text-sm text-muted-foreground mt-2">Automatically save the result to Flojoy Cloud</p>
      <div className="flex flex-col">
        <hr className="my-3" />

        {!isCloudKeySet ? (
          <Button onClick={() => setIsEnvVarModalOpen(true)} className="w-full mt-5">
            Connect to Flojoy Cloud
          </Button>

        ) : (
          <div>

            <h2 className="mb-2 text-lg font-bold text-accent1 ">
              Unit Under Test
            </h2>

            <div className="flex">

              <div className="flex-grow">
                <div className="pb-1 pt-2 text-xs text-muted-foreground">
                  <p>Serial Number</p>
                </div>
                <Input
                  className="focus:ring-accent1 focus:ring-offset-1 focus-visible:ring-accent1 focus-visible:ring-offset-1"
                  type="text"
                  value={serialNumber}
                  onChange={(e) => setSerialNumber(e.target.value)}
                  placeholder="SN-0001"
                  disabled={isLocked}
                  autoFocus
                />
              </div>

              <div className="ml-2 flex-none w-1/3">
                <div className="pb-1 pt-2 text-xs text-muted-foreground">
                  <p>Lot Number</p>
                </div>
                <Input
                  className="focus:ring-accent1 focus:ring-offset-1 focus-visible:ring-accent1 focus-visible:ring-offset-1"
                  type="text"
                  value={lotNumber}
                  onChange={(e) => setLotNumber(e.target.value)}
                  placeholder="L-001"
                  disabled={isLocked}
                  autoFocus
                />
              </div>

            </div>


            <div className="pb-1 pt-2 text-xs text-muted-foreground">
              <p>Part Number</p>
            </div>
            <Select onValueChange={setPartNumber} disabled={isLocked}>
              <SelectTrigger>
                <SelectValue placeholder={"Select a part..."} />
              </SelectTrigger>
              <SelectContent className="max-h-72">
                {dummyPartQuery.map((part) => (
                  <SelectItem key={part} value={part}>
                    {part}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="pt-2 text-xs text-muted-foreground">
              <p>Description: Actuator 62mm </p>
              <p>Product: Arm-Link 6</p>
            </div>

            <hr className="mt-4" />

            <h2 className="my-2 text-lg font-bold text-accent1 ">
              Test Environment
            </h2>

            <div className="pb-1 text-xs text-muted-foreground">
              <p>Test Station</p>
            </div>

            <Select onValueChange={setProjectId} disabled={isLocked}>
              <SelectTrigger>
                <SelectValue placeholder={"Select a test JIG..."} />
              </SelectTrigger>
              <SelectContent className="max-h-72">
                {projectsQuery.data.length === 0 && (
                  <div className="flex flex-col items-center justify-center gap-2 p-2 text-sm">
                    <strong>No projects found</strong>
                    <Button
                      onClick={() => projectsQuery.refetch()}
                      variant={"ghost"}
                    >
                      Refresh part list
                    </Button>
                  </div>
                )}
                {projectsQuery.data.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="mt-2 grid grid-cols-2 grid-flow-row gap-1 text-xs text-muted-foreground">
              <p>Station: ID-12345678 </p>
              <p>Test JIG P/N: PN-0123456</p>
              <p>Test JIG SN: SN-0123456</p>
              <p>Operator: John Doe</p>
              <p> Sequencer: TSW-0.3.0 </p>
              <p> Integrity: {getIntegrity(sequences) ?
                <Badge className="h-4 bg-green-500">Pass</Badge> :
                <Badge className="h-4 bg-red-500">Fail</Badge>}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
