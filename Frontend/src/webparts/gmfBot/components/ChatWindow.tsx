// import './ChatWindow.module.scss';
// import * as React from 'react';

// interface Message {
//   sender: string;
//   text: string;
// }

// export default function ChatWindow({ messages }: { messages: Message[] }) {
//   return (
//     <div className="chat-window">
//       {messages.map((msg, i) => (
//         <div key={i} className={`message ${msg.sender}`}>
//           {msg.text}
//         </div>
//       ))}
//     </div>
//   );
// }

import * as React from 'react';
import styles from './ChatWindow.module.scss'; // Make sure to import styles correctly

// Define a Message type with sender restricted to 'user' or 'bot'
interface Message {
  sender: 'user' | 'bot';
  text: string;
}

interface ChatWindowProps {
  messages: Message[]; // Define the prop to accept messages
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages }) => {
  return (
    <div className='chat-window'> {/* Use CSS Module styles */}
      {messages.map((msg, i) => (
        <div key={i} className={`${styles.message} ${styles[msg.sender]}`}> {/* Apply sender styles dynamically */}
          {msg.text}
        </div>
      ))}
    </div>
  );
};

export default ChatWindow;


// import './ChatWindow.module.scss';
// import * as React from 'react';

// interface Message {
//   sender: string;
//   text: string;
// }

// interface ChatWindowProps {
//   messages: Message[];
// }

// const ChatWindow: React.FC<ChatWindowProps> = ({ messages }): JSX.Element => {
//   return (
//     <div className="chat-window">
//       {messages.map((msg, i) => (
//         <div key={i} className={`message ${msg.sender}`}>
//           {msg.text}
//         </div>
//       ))}
//     </div>
//   );
// };

// export default ChatWindow;
