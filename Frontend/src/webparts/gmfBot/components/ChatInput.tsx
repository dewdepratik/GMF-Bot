// import './ChatInput.module.scss';
// import { useState } from 'react';
// import * as React from 'react';

// export default function ChatInput({ onSend }: { onSend: (msg: string) => void }) {
//   const [input, setInput] = useState('');

//   // const send = async (): void => 
//   const send = async (): Promise<void> =>{
//     if (!input.trim()) return;
//     onSend(input);
//     setInput('');
//   };

//   return (
//     <div className="input-wrapper">
//       <input
//         type="text"
//         value={input}
//         onChange={(e) => setInput(e.target.value)}
//         placeholder="Ask a question or describe what you need"
//         onKeyDown={(e) => e.key === 'Enter' && send()}
//       />
//       <button onClick={send}>➤</button>
//     </div>
//   );
// }

import './ChatInput.module.scss';
import { useState } from 'react';
import * as React from 'react';

export default function ChatInput({ onSend }: { onSend: (msg: string) => void }): JSX.Element {
  const [input, setInput] = useState('');

  // Correctly typed async function with explicit return type of Promise<void>
  const send = async (): Promise<void> => {
    if (!input.trim()) return;
    onSend(input);
    setInput('');
  };

  return (
    <div className="input-wrapper">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask a question or describe what you need"
        onKeyDown={(e) => e.key === 'Enter' && send()}
      />
      <button onClick={send}>➤</button>
    </div>
  );
}

// import './ChatInput.module.scss';
// import { useState } from 'react';
// import * as React from 'react';

// interface ChatInputProps {
//   onSend: (msg: string) => void;
// }

// const ChatInput: React.FC<ChatInputProps> = ({ onSend }): JSX.Element => {
//   const [input, setInput] = useState('');

//   const send = (): void => {
//     if (!input.trim()) return;
//     onSend(input);
//     setInput('');
//   };

//   return (
//     <div className="input-wrapper">
//       <input
//         type="text"
//         value={input}
//         onChange={(e) => setInput(e.target.value)}
//         placeholder="Ask a question or describe what you need"
//         onKeyDown={(e) => e.key === 'Enter' && send()}
//       />
//       <button onClick={send}>➤</button>
//     </div>
//   );
// };

// export default ChatInput;
