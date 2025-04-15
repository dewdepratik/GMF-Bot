// // import * as React from 'react';
// // import styles from './GmfBot.module.scss';
// // import type { IGmfBotProps } from './IGmfBotProps';
// // import { escape } from '@microsoft/sp-lodash-subset';

// // export default class GmfBot extends React.Component<IGmfBotProps> {
// //   public render(): React.ReactElement<IGmfBotProps> {
// //     const {
// //       description,
// //       isDarkTheme,
// //       environmentMessage,
// //       hasTeamsContext,
// //       userDisplayName
// //     } = this.props;

// //     return (
// //       <section className={`${styles.gmfBot} ${hasTeamsContext ? styles.teams : ''}`}>
// //         <div className={styles.welcome}>
// //           <img alt="" src={isDarkTheme ? require('../assets/welcome-dark.png') : require('../assets/welcome-light.png')} className={styles.welcomeImage} />
// //           <h2>Well done, {escape(userDisplayName)}!</h2>
// //           <div>{environmentMessage}</div>
// //           <div>Web part property value: <strong>{escape(description)}</strong></div>
// //         </div>
// //         <div>
// //           <h3>Welcome to SharePoint Framework!</h3>
// //           <p>
// //             The SharePoint Framework (SPFx) is a extensibility model for Microsoft Viva, Microsoft Teams and SharePoint. It&#39;s the easiest way to extend Microsoft 365 with automatic Single Sign On, automatic hosting and industry standard tooling.
// //           </p>
// //           <h4>Learn more about SPFx development:</h4>
// //           <ul className={styles.links}>
// //             <li><a href="https://aka.ms/spfx" target="_blank" rel="noreferrer">SharePoint Framework Overview</a></li>
// //             <li><a href="https://aka.ms/spfx-yeoman-graph" target="_blank" rel="noreferrer">Use Microsoft Graph in your solution</a></li>
// //             <li><a href="https://aka.ms/spfx-yeoman-teams" target="_blank" rel="noreferrer">Build for Microsoft Teams using SharePoint Framework</a></li>
// //             <li><a href="https://aka.ms/spfx-yeoman-viva" target="_blank" rel="noreferrer">Build for Microsoft Viva Connections using SharePoint Framework</a></li>
// //             <li><a href="https://aka.ms/spfx-yeoman-store" target="_blank" rel="noreferrer">Publish SharePoint Framework applications to the marketplace</a></li>
// //             <li><a href="https://aka.ms/spfx-yeoman-api" target="_blank" rel="noreferrer">SharePoint Framework API reference</a></li>
// //             <li><a href="https://aka.ms/m365pnp" target="_blank" rel="noreferrer">Microsoft 365 Developer Community</a></li>
// //           </ul>
// //         </div>
// //       </section>
// //     );
// //   }
// // }


// // import './GmfBot.module.scss';
// // import ChatWindow from './ChatWindow';
// // import ChatInput from './ChatInput';
// // import { useState } from 'react';
// // import * as React from 'react';

// // function App() {
// //   const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);

// //   const handleMessage = (msg: string) => {
// //     setMessages(prev => [...prev, { sender: 'user', text: msg }]);

// //     setTimeout(() => {
// //       setMessages(prev => [...prev, { sender: 'bot', text: `Echo: ${msg}` }]);
// //     }, 800);
// //   };

// //   return (
// //     <div className="chat-only-container">
// //       <ChatWindow messages={messages} />
// //       <ChatInput onSend={handleMessage} />
// //     </div>
// //   );
// // }

// // export default App;


// import * as React from 'react';
// import styles from './GmfBot.module.scss';

// export default function Chatbot(): JSX.Element {
//   const [messages, setMessages] = React.useState<{ sender: string; text: string }[]>([]);
//   const [input, setInput] = React.useState('');

//   const send = () => {
//     if (!input.trim()) return;
//     setMessages(prev => [...prev, { sender: 'user', text: input }]);
//     setInput('');
//     setTimeout(() => {
//       setMessages(prev => [...prev, { sender: 'bot', text: `Echo: ${input}` }]);
//     }, 600);
//   };

//   return (
//     // <div className={styles.chatContainer}>
//     //   <div className={styles.chatWindow}>
//     //     {messages.map((msg, i) => (
//     //       <div key={i} className={`${styles.message} ${styles[msg.sender]}`}>
//     //         {msg.text}
//     //       </div>
//     //     ))}
//     //   </div>
//     //   <div className={styles.inputWrapper}>
//     //     <input
//     //       type="text"
//     //       value={input}
//     //       onChange={(e) => setInput(e.target.value)}
//     //       placeholder="Ask a question or describe what you need"
//     //       onKeyDown={(e) => e.key === 'Enter' && send()}
//     //     />
//     //     <button onClick={send}>➤</button>
//     //   </div>
//     // </div>
//     <div className={styles.chatContainer}>
//   <div className={styles.chatWindow}>
//     {messages.map((msg, i) => (
//      <div key={i} className={`${styles.message} ${styles[msg.sender as 'user' | 'bot']}`}>

//         {msg.text}
//       </div>
//     ))}
//   </div>
//   <div className={styles.inputWrapper}>
//     <input
//       type="text"
//       value={input}
//       onChange={(e) => setInput(e.target.value)}
//       placeholder="Ask a question..."
//       onKeyDown={(e) => e.key === 'Enter' && send()}
//     />
//     <button onClick={send}>➤</button>
//   </div>
// </div>

//   );
// }


// import * as React from 'react';
// import axios from 'axios';
// import styles from './GmfBot.module.scss';

// export default function Chatbot(): JSX.Element {
//   const [messages, setMessages] = React.useState<{ sender: 'user' | 'bot'; text: string }[]>([]);
//   const [input, setInput] = React.useState('');

//   const send = async () => {
//     if (!input.trim()) return;

//     setMessages(prev => [...prev, { sender: 'user', text: input }]);

//     try {
//       const res = await axios.post('http://localhost:8000/chat', { message: input });
//       setMessages(prev => [...prev, { sender: 'bot', text: res.data.response }]);
//     } catch (err) {
//       console.error(err);
//       setMessages(prev => [...prev, { sender: 'bot', text: 'Something went wrong.' }]);
//     }

//     setInput('');
//   };

//   return (
//     <div className={styles.chatContainer}>
//       <div className={styles.chatWindow}>
//         {messages.map((msg, i) => (
//           <div key={i} className={`${styles.message} ${styles[msg.sender]}`}>
//             {msg.text}
//           </div>
//         ))}
//       </div>
//       <div className={styles.inputWrapper}>
//         <input
//           type="text"
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           placeholder="Ask something..."
//           onKeyDown={(e) => e.key === 'Enter' && send()}
//         />
//         <button onClick={send}>➤</button>
//       </div>
//     </div>
//   );
// }

//Pratik code
// import * as React from 'react';
// import axios from 'axios';
// import styles from './GmfBot.module.scss';

// // Define the types for the message structure
// type Message = {
//   sender: 'user' | 'bot';
//   text: string;
// };

// export default function Chatbot(): JSX.Element {
//   const [messages, setMessages] = React.useState<Message[]>([]);
//   const [input, setInput] = React.useState<string>('');

//   // Define send function with explicit return type
//   const send = async (): Promise<void> => {
//     if (!input.trim()) return;  // Do nothing if the input is empty

//     setMessages((prev) => [...prev, { sender: 'user', text: input }]);  // Add user message to state

//     try {
//       // Make API call to the backend
//       const res = await axios.post('http://localhost:8000/chat', { message: input });
      
//       // Assuming the response from the backend has a 'response' property that contains the bot's reply
//       setMessages((prev) => [
//         ...prev, 
//         { sender: 'bot', text: res.data.response || 'No response from bot.' } // Default fallback message
//       ]);
//     } catch (err) {
//       console.error(err);
//       setMessages((prev) => [
//         ...prev, 
//         { sender: 'bot', text: 'Something went wrong. Please try again later.' } // Error message if the API fails
//       ]);
//     }

//     setInput('');  // Clear the input field
//   };

//   return (
//     <div className={styles.chatContainer}>
//       <div className={styles.chatWindow}>
//         {messages.map((msg, i) => (
//           <div key={i} className={`${styles.message} ${styles[msg.sender]}`}>
//             {msg.text} {/* Displaying the message text */}
//           </div>
//         ))}
//       </div>

//       {/* Input and button at the bottom */}
//       <div className={styles.inputWrapper}>
//         <input
//           type="text"
//           value={input}
//           onChange={(e) => setInput(e.target.value)}  // Update input field on change
//           placeholder="Ask something..."
//           onKeyDown={(e) => e.key === 'Enter' && send()}  // Send message on pressing Enter
//         />
//         <button onClick={send}>➤</button> {/* Send button */}
//       </div>
//     </div>
//   );
// }


// import * as React from 'react';
// import axios from 'axios';
// import ReactMarkdown from 'react-markdown';  // Make sure react-markdown is imported
// import styles from './GmfBot.module.scss';

// type Message = {
//   sender: 'user' | 'bot';
//   text: string;
// };

// export default function Chatbot(): JSX.Element {
//   const [messages, setMessages] = React.useState<Message[]>([]);
//   const [input, setInput] = React.useState<string>('');
  
//   const send = async (): Promise<void> => {
//     if (!input.trim()) return;

//     setMessages((prev) => [...prev, { sender: 'user', text: input }]);

//     try {
//       const res = await axios.post('http://localhost:8000/chat', { message: input });

//       // Check if response has valid data
//       if (res.data && res.data.response) {
//         setMessages((prev) => [
//           ...prev,
//           { sender: 'bot', text: res.data.response }  // Ensure this response is in markdown format
//         ]);
//       } else {
//         setMessages((prev) => [
//           ...prev,
//           { sender: 'bot', text: 'No response from bot.' }
//         ]);
//       }
//     } catch (err) {
//       console.error(err);
//       setMessages((prev) => [
//         ...prev,
//         { sender: 'bot', text: 'Something went wrong. Please try again later.' }
//       ]);
//     }

//     setInput('');
//   };

//   return (
//     <div className={styles.chatContainer}>
//       <div className={styles.chatWindow}>
//         {messages.map((msg, i) => (
//           <div key={i} className={`${styles.message} ${styles[msg.sender]}`}>
//             {/* Render the response using react-markdown */}
//             <ReactMarkdown>{msg.text}</ReactMarkdown>  {/* This will render markdown */}
//           </div>
//         ))}
//       </div>

//       <div className={styles.inputWrapper}>
//         <input
//           type="text"
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           placeholder="Ask something..."
//           onKeyDown={(e) => e.key === 'Enter' && send()}
//         />
//         <button onClick={send}>➤</button>
//       </div>
//     </div>
//   );
// }


// import * as React from 'react';
// import axios from 'axios';
// import ReactMarkdown from 'react-markdown'; // Make sure react-markdown is imported
// import styles from './GmfBot.module.scss';

// type Message = {
//   sender: 'user' | 'bot';
//   text: string;
// };

// export default function Chatbot(): JSX.Element {
//   const [messages, setMessages] = React.useState<Message[]>([]);
//   const [input, setInput] = React.useState<string>('');
//   const [contentProcessed, setContentProcessed] = React.useState<boolean>(false); // To track if content has been processed
//   const [isProcessing, setIsProcessing] = React.useState<boolean>(false); // To show loading state for processing

//   // Function to trigger process-content API
//   const processContent = async () => {
//     setIsProcessing(true); // Set loading state while processing content
//     try {
//       // Call your backend API to process content
//       const response = await axios.post('http://localhost:8000/process-content', {
//         process_site_pages: true,
//         process_documents: true,
//         store_name: 'chatbot-store', // Use appropriate store name
//       });

//       // If content is processed, update state to reflect this
//       if (response.data.status === 'success') {
//         setContentProcessed(true);
//         console.log('Content processed successfully!');
//       } else {
//         console.error('Error processing content:', response.data.message);
//       }
//     } catch (error) {
//       console.error('Error calling process-content API:', error);
//     } finally {
//       setIsProcessing(false); // Reset loading state after processing is done
//     }
//   };

//   // Send function
//   const send = async (): Promise<void> => {
//     if (!input.trim()) return;

//     setMessages((prev) => [...prev, { sender: 'user', text: input }]);

//     try {
//       const res = await axios.post('http://localhost:8000/chat', { message: input });

//       // Check if response has valid data
//       if (res.data && res.data.response) {
//         setMessages((prev) => [
//           ...prev,
//           { sender: 'bot', text: res.data.response } // Ensure this response is in markdown format
//         ]);
//       } else {
//         setMessages((prev) => [
//           ...prev,
//           { sender: 'bot', text: 'No response from bot.' }
//         ]);
//       }
//     } catch (err) {
//       console.error(err);
//       setMessages((prev) => [
//         ...prev,
//         { sender: 'bot', text: 'Something went wrong. Please try again later.' }
//       ]);
//     }

//     setInput('');
//   };

//   // Trigger content processing when the component is mounted or based on interaction
//   React.useEffect(() => {
//     if (!contentProcessed) {
//       processContent(); // Automatically trigger content processing on first load or interaction
//     }
//   }, [contentProcessed]);

//   return (
//     <div className={styles.chatContainer}>
//       <div className={styles.chatWindow}>
//         {messages.map((msg, i) => (
//           <div key={i} className={`${styles.message} ${styles[msg.sender]}`}>
//             {/* Render the response using react-markdown */}
//             <ReactMarkdown>{msg.text}</ReactMarkdown> {/* This will render markdown */}
//           </div>
//         ))}
//       </div>

//       {isProcessing && (
//         <div className={styles.processingMessage}>Processing content... Please wait.</div>
//       )}

//       <div className={styles.inputWrapper}>
//         <input
//           type="text"
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           placeholder="Ask something..."
//           onKeyDown={(e) => e.key === 'Enter' && send()}
//         />
//         <button onClick={send}>➤</button>
//       </div>
//     </div>
//   );
// }



import * as React from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown'; // Make sure react-markdown is imported
import styles from './GmfBot.module.scss';

type Message = {
  sender: 'user' | 'bot';
  text: string;
};

export default function Chatbot(): JSX.Element {
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [input, setInput] = React.useState<string>('');
  const [contentProcessed, setContentProcessed] = React.useState<boolean>(false); // To track if content has been processed
  const [isProcessing, setIsProcessing] = React.useState<boolean>(false); // To show loading state for processing

  // Function to trigger process-content API
  const processContent = async (): Promise<void> => {
    setIsProcessing(true); // Set loading state while processing content
    try {
      const response = await axios.post('http://localhost:8000/process-content', {
        process_site_pages: true,
        process_documents: true,
        store_name: 'chatbot-store', // Use appropriate store name
      });

      if (response.data.status === 'success') {
        setContentProcessed(true);
        console.log('Content processed successfully!');
      } else {
        console.error('Error processing content:', response.data.message);
      }
    } catch (error) {
      console.error('Error calling process-content API:', error);
    } finally {
      setIsProcessing(false); // Reset loading state after processing is done
    }
  };

  // Send function with explicit return type and proper async handling
  const send = async (): Promise<void> => { // Explicit return type added
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { sender: 'user', text: input }]);

    try {
      const res = await axios.post('http://localhost:8000/chat', { message: input });

      if (res.data && res.data.response) {
        setMessages((prev) => [
          ...prev,
          { sender: 'bot', text: res.data.response },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { sender: 'bot', text: 'No response from bot.' },
        ]);
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { sender: 'bot', text: 'Something went wrong. Please try again later.' },
      ]);
    }

    setInput('');
  };

  // Trigger content processing when the component is mounted or based on interaction
  React.useEffect(() => {
    if (!contentProcessed) {
      processContent().catch((err) => {
        console.error('Error during content processing:', err); // Handle errors properly
      });
    }
  }, [contentProcessed]);

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatWindow}>
        {messages.map((msg, i) => (
          <div key={i} className={`${styles.message} ${styles[msg.sender]}`}>
            <ReactMarkdown>{msg.text}</ReactMarkdown>
          </div>
        ))}
      </div>

      {isProcessing && (
        <div className={styles.processingMessage}>Processing content... Please wait.</div>
      )}

      <div className={styles.inputWrapper}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something..."
          onKeyDown={(e) => e.key === 'Enter' && send()}
        />
        <button onClick={send}>➤</button>
      </div>
    </div>
  );
}

