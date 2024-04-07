import { MenubarItem, MenubarShortcut } from "@/renderer/components/ui/menubar";
import { useSaveAllSequences } from "@/renderer/hooks/useTestSequencerProject";
import { useTestSequencerState } from "@/renderer/hooks/useTestSequencerState";
import useWithPermission from "@/renderer/hooks/useWithPermission";
import { useSequencerModalStore } from "@/renderer/stores/modal";

export const SaveSequencesButton = () => {
  const handleSave = useSave();

  return (
    <MenubarItem data-testid="btn-save" onClick={handleSave}>
      Save sequences <MenubarShortcut>⌘S</MenubarShortcut>
    </MenubarItem>
  );
};

export const useSave = () => {
  const { withPermissionCheck } = useWithPermission();
  const saveSequences = useSaveAllSequences();
  const { setIsCreateProjectModalOpen } = useSequencerModalStore();
  const { project, sequences } = useTestSequencerState();

  const handleSave = async () => {
    if (project === null && sequences.length === 0) {
      setIsCreateProjectModalOpen(true);
    } else {
      await saveSequences();
    }
  };

  return withPermissionCheck(handleSave);
};
