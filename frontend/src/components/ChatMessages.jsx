export default function ChatMessages({ chatMessages }) {
  return (
    <div className="messages">
      {chatMessages.map((msg) => (
        <div key={msg.id} className={`message ${msg.sender}`}>
          <div className="bubble">{msg.message}</div>
        </div>
      ))}
    </div>
  );
}

