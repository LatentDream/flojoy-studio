import { v4 as uuidv4 } from "uuid";
import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import {
    BackendGlobalState,
  Cycle,
  MsgState,
  TestRootNode,
  TestSequenceContainer,
  TestSequenceElement,
} from "@/renderer/types/test-sequencer";
import { TestSequencerProject } from "@/renderer/types/test-sequencer";

type State = {
  websocketId: string;
  elements: TestSequenceElement[];
  isLocked: boolean;
  isLoading: boolean;
  backendGlobalState: BackendGlobalState;
  cycle: Cycle;
  runs: TestSequenceElement[];
  backendState: MsgState;
  testSequenceUnsaved: boolean;
  testSequenceTree: TestRootNode;
  testSequencerProject: TestSequencerProject | null;
  currentSequence: TestSequencerProject | null;
  sequences: TestSequenceContainer[];
};

type Actions = {
  setWebsocketId: (val: string) => void;
  setElements: (val: TestSequenceElement[]) => void;
  setIsLocked: (val: boolean) => void;
  setIsLoading: (val: boolean) => void;
  setBackendGlobalState: (val: BackendGlobalState) => void;
  setBackendState: (val: MsgState) => void;
  setTestSequenceUnsaved: (val: boolean) => void;
  setTestSequenceTree: (val: TestRootNode) => void;
  setTestSequencerProject: (val: TestSequencerProject | null) => void;
  setCycleCount: (val: number) => void;
  setInfinite: (val: boolean) => void;
  saveRun: () => void;
  previousCycle: () => void;
  nextCycle: () => void;
  clearPreviousRuns: () => void;
  setSequenceAsRunnable: (name: string) => void;
  setNextSequenceAsRunnable: () => void;
};

export const useSequencerStore = create<State & Actions>()(
  immer((set) => ({
    isLocked: false,
    setIsLocked: (val) =>
      set((state) => {
        state.isLocked = val;
      }),

    isLoading: true,
    setIsLoading: (val) =>
      set((state) => {
        state.isLoading = val;
      }),

    curRun: [],
    websocketId: uuidv4(),
    elements: [],
    backendGlobalState: "test_set_done",
    backendState: "test_set_done",
    testSequenceUnsaved: false,
    testSequenceTree: {
      type: "root",
      children: [],
      identifiers: [],
    },
    testSequencerProject: null,
    currentSequence: null,
    sequences: [],


    cycle: {
      infinite: false,
      cycleCount: 1,
      cycleNumber: 0,
      ptrCycle: -1,
    },
    runs: [],
    setCycleCount: (val: number) =>
      set((state) => {
        console.log("setCycleCount", val);
        if (val < 1) {
          state.cycle.cycleCount = 1;
          state.cycle.infinite = true;
        } else {
          state.cycle.cycleCount = val;
          state.cycle.infinite = false;
        }
      }),
    setInfinite: (val: boolean) =>
      set((state) => {
        state.cycle.infinite = val;
      }),
    saveRun: () => 
      set((state) => {
        state.runs.push(state.elements);
        state.cycle.ptrCycle = state.cycle.ptrCycle + 1;
        state.cycle.cycleNumber = state.cycle.cycleNumber + 1;
      }),
    previousCycle: () =>
      set((state) => {
        if (state.runs.length > 0) {
          state.cycle.ptrCycle = state.cycle.ptrCycle - 1;
          if (state.cycle.ptrCycle < 0) {
            state.cycle.ptrCycle = 0;
          }
          state.elements = state.runs[state.cycle.ptrCycle];
        }
      }),
    nextCycle: () =>
      set((state) => {
        if (state.runs.length > 0) {
          state.cycle.ptrCycle = state.cycle.ptrCycle + 1;
          if (state.cycle.ptrCycle >= state.runs.length) {
            state.cycle.ptrCycle = state.runs.length - 1;
          }
          state.elements = state.runs[state.cycle.ptrCycle];
        }
      }),
    clearPreviousRuns: () =>
      set((state) => {
        state.runs = [];
        state.cycle.ptrCycle = -1;
        state.cycle.cycleNumber = 0;
      }),  


    setWebsocketId: (val) =>
      set((state) => {
        state.websocketId = val;
      }),
    setElements: (val) =>
      set((state) => {
        state.elements = val;
      }),

    setBackendState: (val) =>
      set((state) => {
        state.backendState = val;
      }),
    setBackendGlobalState: (val) =>
      set((state) => {
        state.backendGlobalState = val;
      }),
    setTestSequenceUnsaved: (val) =>
      set((state) => {
        state.testSequenceUnsaved = val;
      }),
    setTestSequenceTree: (val) =>
      set((state) => {
        state.testSequenceTree = val;
      }),
    setTestSequencerProject: (val) =>
      set((state) => {
        state.testSequencerProject = val;
        if (val !== null) {
          state.sequences.push({
            project: val,
            cycle: state.cycle,
            tree: state.testSequenceTree,
            elements: state.elements,
          });
        }
      }),

    // Navigation through sequences: TODO set the elems
    setNextSequenceAsRunnable: () =>
      set((state) => {
        if (state.testSequencerProject !== null) {
          const idx = state.sequences.findIndex(
            (seq) => seq.project.name === state.currentSequence?.name,
          );
          if (idx < state.sequences.length - 1) {
            // Save the current state and do the swap
            const currSequence = {
              project: { ...state.testSequencerProject },
              cycle: { ...state.cycle },
              tree: { ...state.testSequenceTree },
              elements: [...state.elements],
            };
            console.log("saving current sequence", currSequence);
            state.sequences[idx] = currSequence;
            state.testSequencerProject = state.sequences[idx + 1].project;
            state.testSequenceTree = state.sequences[idx + 1].tree;
            state.elements = state.sequences[idx + 1].elements;
            state.cycle = state.sequences[idx + 1].cycle;
          }
        }
      }),

    setSequenceAsRunnable: (name) =>
      set((state) => {
        if (state.testSequencerProject !== null) {
          const idx = state.sequences.findIndex(
            (seq) => seq.project.name === name);
          const oldIdx = state.sequences.findIndex(
            (seq) => seq.project.name === state.testSequencerProject.name);
          const currSequence = {
            project: { ...state.testSequencerProject },
            cycle: { ...state.cycle },
            tree: { ...state.testSequenceTree },
            elements: [...state.elements],
          };
          state.sequences[oldIdx] = currSequence;
          state.testSequencerProject = state.sequences[idx].project;
          state.testSequenceTree = state.sequences[idx].tree;
          state.elements = state.sequences[idx].elements;
          state.cycle = state.sequences[idx].cycle;

          
        }
      }),


  })),
);
