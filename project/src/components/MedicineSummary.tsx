import React from 'react';
import { motion } from 'framer-motion';
import { Heart, AlertCircle } from 'lucide-react';
import type { MedicineResponse } from '../types';

interface MedicineSummaryProps {
  medicine: MedicineResponse;
  onConfirm: (confirmed: boolean) => void;
}

export const MedicineSummary: React.FC<MedicineSummaryProps> = ({ medicine, onConfirm }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-lg shadow-xl p-6 max-w-2xl mx-auto mt-8"
    >
      <div className="flex gap-6">
        <div className="w-1/3">
          <img
            src={medicine.image_url}
            alt={medicine.generic_name}
            className="w-full h-auto rounded-lg shadow-md"
          />
        </div>
        <div className="w-2/3">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            {medicine.generic_name}
          </h2>
          <p className="text-gray-600 mb-4">Imprint: {medicine.imprint_number}</p>
          <p className="text-gray-700 mb-6">{medicine.summary}</p>
          
          <div className="border-t pt-4">
            <p className="text-lg font-medium text-gray-800 mb-4">
              Is this the right pill for your condition?
            </p>
            <div className="flex gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onConfirm(true)}
                className="flex-1 bg-pink-500 text-white py-2 px-4 rounded-full flex items-center justify-center gap-2 hover:bg-pink-600 transition-colors"
              >
                <Heart className="w-5 h-5" />
                Yes, that's correct
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onConfirm(false)}
                className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-full flex items-center justify-center gap-2 hover:bg-gray-200 transition-colors"
              >
                <AlertCircle className="w-5 h-5" />
                No, that's not it
              </motion.button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};