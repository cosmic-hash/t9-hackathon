import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send } from 'lucide-react';
import type { ChatResponse } from '../types';

interface ChatInterfaceProps {
  onSendMessage: (message: string) => Promise<void>;
  messages: ChatResponse[];
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ onSendMessage, messages }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      await onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-2xl mx-auto mt-8 bg-white rounded-lg shadow-xl"
    >
      <div className="h-[400px] overflow-y-auto p-6">
        {messages.map((msg, index) => (
          <div key={index} className="mb-4">
            {/* Render User Query only if it's not part of the response */}
            {msg.user_query && index === 0 || (index > 0 && messages[index - 1].user_query !== msg.user_query) ? (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-right"
              >
                <div className="inline-block rounded-lg px-4 py-2 max-w-[80%] bg-pink-500 text-white">
                  <p>{msg.user_query}</p>
                </div>
              </motion.div>
            ) : null}

            {/* Bot Response (Left Side) */}
            {msg.explanation && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-left mt-2"
              >
                <div className="inline-block rounded-lg px-4 py-2 max-w-[80%] bg-rose-100 text-black">
                  <p className="mb-1">{msg.explanation}</p>
                  {msg.generic_name && (
                    <p className="text-sm text-black-600">
                      <strong>Generic Name:</strong> {msg.generic_name}
                    </p>
                  )}
                  {msg.imprint_number && (
                    <p className="text-sm text-black-600">
                      <strong>Imprint Number:</strong> {msg.imprint_number}
                    </p>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask about your medication..."
            className="flex-1 px-4 py-2 border rounded-full focus:outline-none focus:ring-2 focus:pink-300"
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            type="submit"
            className="bg-pink-500 text-white p-2 rounded-full hover:bg-pink-600 transition-colors"
          >
            <Send className="w-5 h-5" />
          </motion.button>
        </div>
      </form>
    </motion.div>
  );
};