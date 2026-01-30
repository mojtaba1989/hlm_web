import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LiveFeed from "./LiveFeed";
import FolderBrowser from "./components/RecordingsBrowser";
import ConfigPage from "./Config";
import './App.css'

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LiveFeed />} />
        <Route path="/records" element={<FolderBrowser />} />
        <Route path="/config" element={<ConfigPage />} />
        {/* <Route path="/dashboard/:recordingId" element={<Dashboard />} /> */}
      </Routes>
    </Router>
  );
}
