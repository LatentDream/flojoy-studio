import { Button } from "@/renderer/components/ui/button";
import { Checkbox } from "@/renderer/components/ui/checkbox";
import { Dialog, DialogContent } from "@/renderer/components/ui/dialog";
import { Separator } from "@/renderer/components/ui/separator";
import { useDiscoverAndImportTests } from "@/renderer/hooks/useTestImport";
import { useDisplayedSequenceState } from "@/renderer/hooks/useTestSequencerState";
import { useAppStore } from "@/renderer/stores/app";
import { useSequencerModalStore } from "@/renderer/stores/modal";
import { ExternalLinkIcon } from "lucide-react";
import { useState } from "react";
import { useShallow } from "zustand/react/shallow";

export type ImportTestSettings = {
  importAsOneRef: boolean;
  importType: ImportType;
};

export type discoverableTestTypes = "pytest" | "robotframework";
export type ImportType = discoverableTestTypes | "python";

export const ImportTestModal = () => {
  const { isImportTestModalOpen, setIsImportTestModalOpen } =
    useSequencerModalStore();
  const [checked, setChecked] = useState<boolean>(false);

  const { setIsDepManagerModalOpen } = useAppStore(
    useShallow((state) => ({
      setIsDepManagerModalOpen: state.setIsDepManagerModalOpen,
    })),
  );

  const openFilePicker = useDiscoverAndImportTests();
  const { setIsLocked } = useDisplayedSequenceState();

  const handleImportTest = (importType: ImportType) => {
    setIsLocked(true);
    openFilePicker(
      {
        importType: importType,
        importAsOneRef: checked,
      },
      setIsImportTestModalOpen,
    );
    setIsLocked(false);
  };

  return (
    <Dialog
      open={isImportTestModalOpen}
      onOpenChange={setIsImportTestModalOpen}
    >
      <DialogContent>
        <h2 className="text-lg font-bold text-accent1">Import Tests</h2>
        <Button
          variant={"outline"}
          onClick={() => handleImportTest("pytest")}
          data-testid="pytest-btn"
        >
          Pytest & Unittest
        </Button>
        <Button
          variant={"outline"}
          onClick={() => handleImportTest("robotframework")}
          data-testid="robot-btn"
        >
          Robot Framework
        </Button>
        <Button variant={"outline"} onClick={() => handleImportTest("python")}>
          Python Script
        </Button>
        <Separator />
        <div className="flex justify-between">
          <div className="flex items-center space-x-2 text-xs">
            <Checkbox
              checked={checked}
              onCheckedChange={(checked) => {
                setChecked(checked as boolean);
              }}
            />
            <label>Import all tests as one test</label>
          </div>
          <div className="justify-end">
            <Button
              variant={"link"}
              onClick={() => setIsDepManagerModalOpen(true)}
            >
              <ExternalLinkIcon size={15} className="mr-1" /> Dependency Manager
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
