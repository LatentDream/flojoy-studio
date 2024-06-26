import { TestDiscoverContainer } from "@/renderer/types/test-sequencer";
import {
  createNewTest,
  useDisplayedSequenceState,
} from "./useTestSequencerState";
import { map } from "lodash";
import {
  ImportTestSettings,
  discoverableTestTypes as DiscoverableTestTypes,
} from "@/renderer/routes/test_sequencer_panel/components/modals/ImportTestModal";
import { toast } from "sonner";
import { useCallback } from "react";
import { discoverPytest, discoverRobot } from "@/renderer/lib/api";
import { useSequencerModalStore } from "../stores/modal";
import { toastResultPromise } from "../utils/report-error";
import { Result, err, ok } from "neverthrow";
import { match } from "ts-pattern";

function parseDiscoverContainer(
  data: TestDiscoverContainer,
  settings: ImportTestSettings,
) {
  return map(data.response, (container) => {
    const new_elem = createNewTest({
      name: container.testName,
      path: container.path,
      type: settings.importType,
      args:
        settings.importType === "robotframework" && !settings.importAsOneRef
          ? [container.testName]
          : undefined,
    });
    return new_elem;
  });
}

export const useDiscoverAndImportTests = () => {
  const { addNewElems } = useDisplayedSequenceState();
  const { openErrorModal } = useSequencerModalStore();

  const handleUserDepInstall = useCallback(async (depName: string) => {
    const promise = () => window.api.poetryInstallDepUserGroup(depName);
    toast.promise(promise, {
      loading: `Installing ${depName}...`,
      success: () => {
        return `${depName} has been added.`;
      },
      error:
        "Could not install the library. Please consult the Dependency Manager in the settings.",
    });
  }, []);

  async function getTests(
    path: string,
    settings: ImportTestSettings,
    setModalOpen: (val: boolean) => void,
  ): Promise<Result<void, Error>> {
    const dataResponse = await match(settings.importType)
      .with("python", async () => {
        return ok({
          response: [{ testName: path, path: path }],
          missingLibraries: [],
          error: null,
        });
      })
      .with(
        "pytest",
        async () => await discoverPytest(path, settings.importAsOneRef),
      )
      .with(
        "robotframework",
        async () => await discoverRobot(path, settings.importAsOneRef),
      )
      .exhaustive();
    if (dataResponse.isErr()) {
      return err(dataResponse.error);
    }
    const data = dataResponse.value;
    if (data.error) {
      return err(Error(data.error));
    }
    for (const lib of data.missingLibraries) {
      toast.error(`Missing Python Library: ${lib}`, {
        action: {
          label: "Install",
          onClick: () => {
            handleUserDepInstall(lib);
          },
        },
      });
      return err(Error("Please retry after installing the missing libraries."));
    }
    const newElems = parseDiscoverContainer(data, settings);
    if (newElems.length === 0) {
      return err(Error("No tests were found in the specified file."));
    }
    const result = await addNewElems(newElems);
    if (result.isErr()) {
      return err(result.error);
    }
    setModalOpen(false);
    return ok(undefined);
  }

  const openFilePicker = (
    settings: ImportTestSettings,
    setModalOpen: (val: boolean) => void,
  ) => {
    window.api
      .openTestPicker()
      .then((result) => {
        if (!result) return;
        const { filePath } = result;
        toastResultPromise(getTests(filePath, settings, setModalOpen), {
          loading: "Importing test...",
          success: () => {
            return "Test Imported.";
          },
          error: (e) => {
            // If message too long, open a Error modal instead (with the click of a button)
            if (e.message.length > 100) {
              toast("Error while attempting to discover tests", {
                action: {
                  label: "More details",
                  onClick: () => {
                    openErrorModal(e.message);
                  },
                },
              });
              return "Failed to discover tests due to an unexpected error.";
            }
            return `Error while attempting to discover tests: ${e.message.replace("Error: ", "")}`;
          },
        });
      })
      .catch((error) => {
        console.error("Errors when trying to load file: ", error);
      });
  };

  return openFilePicker;
};

export const useDiscoverElements = () => {
  const handleUserDepInstall = useCallback(async (depName: string) => {
    const promise = () => window.api.poetryInstallDepUserGroup(depName);
    toast.promise(promise, {
      loading: `Installing ${depName}...`,
      success: () => {
        return `${depName} has been added.`;
      },
      error:
        "Could not install the library. Please consult the Dependency Manager in the settings.",
    });
  }, []);

  async function getTests(path: string) {
    let res: Result<TestDiscoverContainer, Error>;
    let type: DiscoverableTestTypes;
    if (path.endsWith(".robot")) {
      res = await discoverRobot(path, false);
      type = "robotframework";
    } else {
      res = await discoverPytest(path, false);
      type = "pytest";
    }
    if (res.isErr()) {
      return err(res.error);
    }
    const data = res.value;
    if (data.error) {
      return err(Error(data.error));
    }
    for (const lib of data.missingLibraries) {
      toast.error(`Missing Python Library: ${lib}`, {
        action: {
          label: "Install",
          onClick: () => {
            handleUserDepInstall(lib);
          },
        },
      });
      return err(Error("Please retry after installing the missing libraries."));
    }
    const newElems = parseDiscoverContainer(data, {
      importAsOneRef: false,
      importType: type,
    });
    if (newElems.length === 0) {
      return err(Error("No tests were found in the specified file."));
    }
    return ok(newElems);
  }

  return getTests;
};
