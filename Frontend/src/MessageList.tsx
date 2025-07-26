import React, { useContext } from "react";
import { ChatContext } from "../state/ChatContext";
import Message from "./Message";

const MessageList: React.FC = () => {
  const { state } = useContext(ChatContext);

  return (
    <div className="message-list">
      {state.messages.map((msg) => (
        <Message key={msg.id} message={msg} />
      ))}
    </div>
  );
};

export default MessageList;
