import React from "react";

type MessageProps = {
  message: {
    id: string;
    sender: "user" | "ai";
    text: string;
    timestamp: string;
  };
};

const Message: React.FC<MessageProps> = ({ message }) => (
  <div className={`message ${message.sender}`}>
    <div className="message-text">{message.text}</div>
    <span className="timestamp">{message.timestamp}</span>
  </div>
);

export default Message;
