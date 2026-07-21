import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ChatWorkspace } from "./chat-workspace";


describe("ChatWorkspace", () => {
  it("submits the entered query", async () => {
    const execute = vi.fn().mockResolvedValue({
      run_id: "run-1",
      final_answer: "done",
      evidence_count: 3,
    });

    render(<ChatWorkspace executeRun={execute} />);
    fireEvent.change(screen.getByLabelText("Question"), {
      target: { value: "leave policy" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByText("done")).toBeInTheDocument();
    expect(execute).toHaveBeenCalledWith("leave policy");
  });
});
