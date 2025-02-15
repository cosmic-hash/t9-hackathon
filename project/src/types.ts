export interface MedicineResponse {
  imprint_number: string;
  generic_name: string;
  summary: string;
  image_url: string;
}

export interface ChatResponse {
  explanation?: string;
  generic_name: string;
  imprint_number?: string;
  user_query?: string;
  message?: string;
  new_purpose?: string;
}

export interface ConversationRequest {
  imprint_number: string;
  generic_name: string;
  user_query: string;
  not_this_pill: boolean;
}