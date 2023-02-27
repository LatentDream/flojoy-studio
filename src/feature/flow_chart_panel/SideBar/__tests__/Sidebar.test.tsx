import { render, fireEvent, waitFor } from "@testing-library/react";
import React, { Dispatch } from "react";
import Sidebar from "../Sidebar";

const theme = "dark";

class ResizeObserver {
  observe() {}
  unobserve() {}
}

jest.mock("../../manifest/COMMANDS_MANIFEST", () => {
  return {
    COMMANDS: [],
    SECTIONS: [],
  };
});

jest.mock("../../manifest/PARAMETERS_MANIFEST", () => {
  return {
    FUNCTION_PARAMETERS: {},
  };
});

const mockChildComponent = jest.fn();
jest.mock("../SidebarSection", () => (props) => {
  mockChildComponent(props);
  return <div />;
});

window.ResizeObserver = ResizeObserver as any;

describe("Sidebar", () => {
  it("should render the component correctly", () => {
    const { container } = render(<Sidebar appTheme={theme} />);
    expect(container).toMatchSnapshot();
  });

  it("checks the add button to be in the document", () => {
    const { container, getByTestId } = render(<Sidebar appTheme={theme} />);
    const addButton: any = getByTestId("add-node-button");

    expect(addButton).toBeInTheDocument();
  });

  it("fires The click event in add node, and checks if the classname of the navbar changes or not", () => {
    const { container, getByTestId } = render(<Sidebar appTheme={theme} />);

    const addButton = getByTestId("add-node-button");

    const sidebar = getByTestId("sidebar");
    expect(sidebar).toHaveStyle("left:-25%");

    fireEvent.click(addButton);

    expect(sidebar).toHaveStyle("left:0%");
  });

  it("fires an Input event and checks if the textInput state changes or not", async () => {
    const { container, getByTestId, getByDisplayValue, getByRole, getByText } =
      render(<Sidebar appTheme={theme} />);
    const input: any = getByTestId("sidebar-input");
    fireEvent.change(input, { target: { value: "sine" } });
    expect(input.value).toBe("sine");
  });
});
