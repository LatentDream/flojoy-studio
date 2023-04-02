import { renderHook } from "@testing-library/react-hooks";
import { useResultsTabEffects } from "@src/feature/results_panel/ResultsTabEffects";
import { ResultTabStateReturnType } from "@src/feature/results_panel/ResultsTabState";
import { NOISY_SINE } from "@src/data/RECIPES";
import { Node } from "reactflow";
import { ElementsData } from "@src/feature/flow_chart_panel/types/CustomNodeProps";
import { ResultIO } from "@src/feature/results_panel/types/ResultsType";

describe("useResultsTabEffects", () => {
  const setResultNodes = jest.fn();
  const nodeResults: ResultIO[] = [
    {
      cmd: "SINE",
      id: "TEST_ID",
      result: {
        type: "bar",
        x: [1, 2, 3],
        y: [1, 2, 3],
      },
    },
  ];
  const nodes: ResultTabStateReturnType["nodes"] = (
    NOISY_SINE.nodes as Node<ElementsData>[]
  ).map((node) => ({
    ...node,
    type: "default",
    position: node.position,
    data: {
      ...node.data,
      resultData: undefined,
    },
  }));
  const resultTabState: ResultTabStateReturnType & { nodeResults: ResultIO[] } =
    {
      resultNodes: [],
      setResultNodes,
      nodes,
      nodeResults: [],
    };

  afterEach(() => {
    jest.resetAllMocks();
  });

  it("should set result nodes correctly", () => {
    renderHook(() => useResultsTabEffects({ ...resultTabState, nodeResults }));
    expect(setResultNodes).toHaveBeenCalledWith(nodes);
  });

  it("should not set result nodes if nodeResults is empty", () => {
    renderHook(() => useResultsTabEffects(resultTabState));
    expect(setResultNodes).not.toHaveBeenCalled();
  });

  it("should not set result nodes if nodes is empty", () => {
    renderHook(() =>
      useResultsTabEffects({ ...resultTabState, nodeResults: [] })
    );
    expect(setResultNodes).not.toHaveBeenCalled();
  });
});