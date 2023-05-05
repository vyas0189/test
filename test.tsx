import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AppId } from "./AppId";

describe("AppId component", () => {
  test("renders the instance ID passed as a prop", () => {
    render(
      <AppId appUrl="http://example.com" instanceId="abc123:def456" />
    );
    expect(screen.getByRole("button")).toHaveTextContent("def456");
  });

  test("calls getInstanceID with the correct argument", () => {
    const mockGetInstanceID = jest.fn(() => "mock instance ID");
    const instanceId = "abc123:def456";
    render(
      <AppId
        appUrl="http://example.com"
        instanceId={instanceId}
      />
    );
    expect(mockGetInstanceID).toHaveBeenCalledWith(instanceId);
  });

  test("renders nothing when instanceId prop is an empty string", () => {
    render(<AppId appUrl="http://example.com" instanceId="" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  test("renders nothing when appUrl prop is an empty string", () => {
    render(<AppId appUrl="" instanceId="abc123:def456" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  test("renders a link to the appUrl with correct attributes", () => {
    const appUrl = "http://example.com";
    render(<AppId appUrl={appUrl} instanceId="abc123:def456" />);
    const button = screen.getByRole("button");
    expect(button).toHaveAttribute("href", appUrl);
    expect(button).toHaveAttribute("target", "_blank");
    expect(button).toHaveAttribute("rel", "noopener noreferrer");
  });

  test("opens the link in a new tab when clicked", () => {
    const appUrl = "http://example.com";
    render(<AppId appUrl={appUrl} instanceId="abc123:def456" />);
    const button = screen.getByRole("button");
    userEvent.click(button);
    expect(window.open).toHaveBeenCalledWith(appUrl, "_blank");
  });
});
