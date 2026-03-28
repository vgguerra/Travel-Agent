export interface TravelState {
  weather: string | null;
  tourism: string | null;
  transport: string | null;
  accommodation: string | null;
  departure_city: string | null;
  destination_city: string | null;
  departure_date: string | null;
  return_date: string | null;
  adults: string | null;
  trip_type: string | null;
  rooms: number | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  state?: TravelState;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  state: TravelState;
}
