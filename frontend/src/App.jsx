import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LiveFeed from "./LiveFeed";
import FolderBrowser from "./components/RecordingsBrowser";
import ConfigEditor from "./Config";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LiveFeed />} />
        <Route path="/records" element={<FolderBrowser />} />
        <Route path="/config" element={<ConfigEditor />} />
      </Routes>
    </Router>
  );
}

