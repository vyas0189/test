import React from "react";
import { render, fireEvent } from "@testing-library/react";
import { AppId } from "./AppId";
import { getInstanceID } from "../../utils/columnHelper";

describe("AppId component", () => {
  it("renders nothing if appUrl or instanceId is empty", () => {
    const { container } = render(<AppId appUrl="" instanceId="" />);
    expect(container.firstChild).toBeNull();
  });

  it("renders a Button with the correct props and instanceId label", () => {
    const appUrl = "https://example.com/app";
    const instanceId = "abc123";
    const { getByRole } = render(<AppId appUrl={appUrl} instanceId={instanceId} />);

    const button = getByRole("link");
    expect(button).toHaveAttribute("href", appUrl);
    expect(button).toHaveAttribute("target", "_blank");
    expect(button).toHaveAttribute("rel", "noopener noreferrer");
    expect(button).toHaveTextContent(instanceId);
  });

  it("calls the getInstanceID function with the instanceId prop", () => {
    const appUrl = "https://example.com/app";
    const instanceId = "abc123";
    jest.spyOn(columnHelper, "getInstanceID");

    render(<AppId appUrl={appUrl} instanceId={instanceId} />);

    expect(columnHelper.getInstanceID).toHaveBeenCalledWith(instanceId);
  });

  it("renders a Button with the correct href when clicked", () => {
    const appUrl = "https://example.com/app";
    const instanceId = "abc123";
    const { getByRole } = render(<AppId appUrl={appUrl} instanceId={instanceId} />);

    const button = getByRole("link");
    fireEvent.click(button);

    expect(button).toHaveAttribute("href", appUrl);
  });

  it("renders a Button with the correct instanceId label when clicked", () => {
    const appUrl = "https://example.com/app";
    const instanceId = "abc123";
    const { getByRole } = render(<AppId appUrl={appUrl} instanceId={instanceId} />);

    const button = getByRole("link");
    fireEvent.click(button);

    expect(button).toHaveTextContent(instanceId);
  });

  it("does not call the getInstanceID function if instanceId is not provided", () => {
    const appUrl = "https://example.com/app";
    jest.spyOn(columnHelper, "getInstanceID");

    render(<AppId appUrl={appUrl} instanceId="" />);

    expect(columnHelper.getInstanceID).not.toHaveBeenCalled();
  });
});
