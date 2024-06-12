import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import './Chat.css'

type Message = {
    role: string;
    content: string;
};

const Chat = () => {
    const [messages, setMessages] = useState<Message[]>([{
        role: 'bot',
        content: 'Welcome to DDQ Chat. Please enter your questions about Parus Finance Ltd.'
    }]);
    const [query, setQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false); // New state to track loading
    const chatBoxRef = useRef<HTMLDivElement>(null);

    const sendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
        setQuery('');


        e.preventDefault();
        const userMessage = { role: 'user', content: query };
        setMessages([...messages, userMessage]);

        setIsLoading(true); // Start loading
        try {
            const response = await fetch('http://localhost:8000/api/response/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query }),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setIsLoading(false); // Stop loading
            const botMessage: Message = { role: 'bot', content: data.response };

            setMessages(messages => [...messages, botMessage]);
        } catch (error) {
            console.error('Error fetching response:', error);
            const errorMessage = { role: 'bot', content: 'Error getting response. Please try again.' };
            setIsLoading(false); // Stop loading in case of error
            setMessages([...messages, userMessage, errorMessage]);
        }


    };

    useEffect(() => {
        if (chatBoxRef.current) {
            chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight; // Auto-scroll to the bottom
        }
    }, [messages]);

    return (
        <div>
            <div className="chat-box">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.role}`}>
                        {msg.content}
                    </div>
                ))}
                {isLoading && <div className="message.typing">...</div>} {/* Typing indicator */}
                <form onSubmit={sendMessage}>
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Enter DDQ Query..."
                        autoFocus
                    />
                    <button type="submit">Send</button>
                </form>
            </div>


        </div>
    );
};

export default Chat;
