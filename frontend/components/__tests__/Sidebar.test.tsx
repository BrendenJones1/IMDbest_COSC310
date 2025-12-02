import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Sidebar } from "../Sidebar";
import { vi } from "vitest";

describe("Sidebar admin visibility", () => {
  it("hides the Admin tab for non-admin users", () => {
    render(<Sidebar activeSection="home" onSectionChange={() => {}} isAdmin={false} />);

    expect(screen.queryByText("Admin")).toBeNull();
  });

  it("shows the Admin tab for admins and handles clicks", async () => {
    const onSectionChange = vi.fn();
    render(<Sidebar activeSection="home" onSectionChange={onSectionChange} isAdmin />);

    const adminButton = screen.getByRole("button", { name: /Admin/i });
    expect(adminButton).toBeVisible();

    await userEvent.click(adminButton);
    expect(onSectionChange).toHaveBeenCalledWith("admin");
  });
});
