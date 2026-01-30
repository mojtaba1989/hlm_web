import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./Home";
import FolderBrowser from "./components/RecordingsBrowser";
import ConfigPage from "./Config";
import './App.css'

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/records" element={<FolderBrowser />} />
        <Route path="/config" element={<ConfigPage />} />
      </Routes>
    </Router>
  );
}
