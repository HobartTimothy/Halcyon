import { ChatWorkspace } from "@/features/chat/components/chat-workspace";
import { executeDemoRun } from "@/lib/api/client";

export default function ChatPage() {
  return (
    <main>
      <ChatWorkspace executeRun={executeDemoRun} />
    </main>
  );
}
