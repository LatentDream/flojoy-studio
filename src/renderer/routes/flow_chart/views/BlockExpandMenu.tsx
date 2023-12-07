import { NodeResult } from "@src/routes/common/types/ResultsType";
// import { useFlowChartState } from "@src/hooks/useFlowChartState";
import { Node } from "reactflow";
import { ElementsData } from "@src/types";
import BlockModal from "./BlockModal";
import { useEffect, useState } from "react";
// import { useFlowChartTabState } from "../FlowChartTabState";

type BlockExpandMenuProps = {
  modalIsOpen: boolean;
  setModalOpen: (open: boolean) => void;
  nodeResults: NodeResult[];
  selectedNode: Node<ElementsData> | null;
  pythonString: string;
  blockFilePath: string;
};

export const BlockExpandMenu = ({
  nodeResults,
  ...props
}: BlockExpandMenuProps) => {
  const { selectedNode } = props;
  const [nodeResult, setNodeResult] = useState<NodeResult | null>(null);
  // const onSelectionChange = () => {
  //   if (!selectedNode) {
  //     setIsExpandMode(false);
  //   }
  // };

  // useOnSelectionChange({ onChange: onSelectionChange });

  useEffect(() => {
    setNodeResult(
      nodeResults.find((node) => node.id === selectedNode?.id) ?? null,
    );
  }, [selectedNode, nodeResults]);

  return (
    <div className="relative" data-testid="node-modal">
      {selectedNode && (
        <BlockModal
          {...props}
          nd={nodeResult}
          selectedNode={selectedNode}
          data-testid="expand-menu"
        />
      )}
    </div>
  );
};