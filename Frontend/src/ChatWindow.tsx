import React from "react";
import MessageList from "./MessageList";
import UserInput from "./UserInput";
import ConversationHistoryPanel from "./ConversationHistoryPanel";

const ChatWindow: React.FC = () => {
  return (
    <div className="chat-window">
      <ConversationHistoryPanel />
      <div className="chat-main">
        <MessageList />
        <UserInput />
      </div>
    </div>
  );
};

export default ChatWindow;
