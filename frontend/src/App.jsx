import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LiveFeed from "./LiveFeed";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LiveFeed />} />
        {/* <Route path="/dashboard/:recordingId" element={<Dashboard />} /> */}
      </Routes>
    </Router>
  );
}