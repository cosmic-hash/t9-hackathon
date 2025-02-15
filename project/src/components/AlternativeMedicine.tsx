import React from 'react';
import { motion } from 'framer-motion';
import { Pill } from 'lucide-react';
import type { ChatResponse } from '../types';

interface AlternativeMedicineProps {
  alternative: ChatResponse;
}

export const AlternativeMedicine: React.FC<AlternativeMedicineProps> = ({ alternative }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-2xl mx-auto mt-8 bg-white rounded-lg shadow-xl p-6"
    >
      <div className="flex items-start gap-4">
        <div className="bg-pink-100 p-3 rounded-full">
          <Pill className="w-6 h-6 text-pink-500" />
        </div>
        <div>
          <motion.h3
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-xl font-semibold text-gray-800 mb-2"
          >
            {alternative.generic_name}
          </motion.h3>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-gray-600"
          >
            {alternative.new_purpose}
          </motion.p>
        </div>
      </div>
    </motion.div>
  );
};