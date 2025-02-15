import React, { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Heart } from 'lucide-react';
import { ImageUploader } from './components/ImageUploader';
import { MedicineSummary } from './components/MedicineSummary';
import { ChatInterface } from './components/ChatInterface';
import { AlternativeMedicine } from './components/AlternativeMedicine';
import type { MedicineResponse, ChatResponse } from './types';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [medicine, setMedicine] = useState<MedicineResponse | null>(null);
  const [showChat, setShowChat] = useState(false);
  const [showAlternative, setShowAlternative] = useState(false);
  const [messages, setMessages] = useState<ChatResponse[]>([]);
  const [alternative, setAlternative] = useState<ChatResponse | null>(null);

  const handleImageUpload = async (file: File) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await axios.post('http://localhost:6969/extract_imprint', formData);
      console.log(response)
      setMedicine(response.data);
    } catch (error) {
      console.error('Error uploading image:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmation = async (confirmed: boolean) => {
    if (confirmed) {
      setShowChat(true);
      setShowAlternative(false);
    } else {
      try {
        const response = await axios.post('http://localhost:6969/conversation', {
          imprint_number: medicine?.imprint_number,
          generic_name: medicine?.generic_name,
          user_query: 'What is this pill used for?',
          not_this_pill: true,
        });
        setAlternative(response.data);
        setShowAlternative(true);
        setShowChat(false);
      } catch (error) {
        console.error('Error getting alternative:', error);
      }
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!medicine) return;

    try {
      const newMessage: ChatResponse = { user_query: message, generic_name: medicine.generic_name };
      setMessages((prev) => [...prev, newMessage]);

      const response = await axios.post('http://localhost:6969/conversation', {
        imprint_number: medicine.imprint_number,
        generic_name: medicine.generic_name,
        user_query: message,
        not_this_pill: false,
      });

      setMessages((prev) => [...prev, response.data]);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 to-red-50 py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <div className="flex justify-center items-center gap-2 mb-4">
          <Heart className="w-8 h-8 text-pink-500" />
          <h1 className="text-4xl font-bold text-gray-800">Pills mate</h1>
        </div>
        <p className="text-gray-600 max-w-xl mx-auto">
          Upload a photo of your medication, and we'll help you identify it and answer any questions you may have.
        </p>
      </motion.div>

      {!medicine && <ImageUploader onImageUpload={handleImageUpload} isLoading={isLoading} />}

      {medicine && !showChat && !showAlternative && (
        <MedicineSummary medicine={medicine} onConfirm={handleConfirmation} />
      )}

      {showChat && <ChatInterface onSendMessage={handleSendMessage} messages={messages} />}

      {showAlternative && alternative && <AlternativeMedicine alternative={alternative} />}
    </div>
  );
}

export default App;