import { use, useEffect, useState } from "react";
import { homeStyles } from "../styles/home_style";

function TestCatalog() {
  const [testCatalog, setTestCatalog] = useState([]);
  const backendUrl = import.meta.env.VITE_BACKEND_URL;
  const [test, setTest] = useState("");
  const [autoEnabled, setAutoEnabled] = useState(false);

  useEffect(() => {
    fetch(`${backendUrl}/api/test_catalog`, { method: "GET" }).
    then(res => res.json()).
    then(data => setTestCatalog(data.scenarios)).
    catch(err => console.error("Failed to fetch test catalog:", err));
    }, []);
    
  useEffect(() => {
    fetch(`${backendUrl}/api/set_scenario`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ "scenario": test }),
    });
  }, [test]);

  useEffect(() => {
    fetch(`${backendUrl}/api/postprocess_toggle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ "enabled": autoEnabled }),
    });
  }, [autoEnabled]);
    
  return (
    <div style={{ display: 'flex',
                  flexDirection: 'column', 
                  alignItems: 'left',
                  marginLeft: '20px',
                  marginRight: '10px',
    }}>
      <div style={{
        // margin: '10px',
        padding: '10px',
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        width: '100%' // Ensures it spans the full width of the parent
      }}>
        <p style={{ fontWeight: 'bold', color: '#888', margin: 0 }}>
          Test Catalog
        </p>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <p style={{ fontWeight: 'bold', color: '#888', margin: 0 }}>
            Auto Post?Process?
          </p>
          <input 
            type="checkbox" 
            onChange={(e) => setAutoEnabled(e.target.checked)} 
            style={{ cursor: 'pointer' }}
            title="Enables post-process after each recording"
          />
        </div>
      </div>
      
      <select 
        onChange={(e) => setTest(e.target.value)} 
        style={{ padding: '8px', borderRadius: '4px' }}
      >
        <option value="" disabled>Select a test...</option>
        {Array.isArray(testCatalog) && testCatalog.map((desc, index) => (
          <option key={index} value={index}>
            {index+1} - {desc}
          </option>
        ))}
      </select>
      <div style={{ ...homeStyles.placeholder, flex: 1, overflowY: 'auto' }}>
      </div>
      <div style={{ fontSize: '0.8rem', color: '#aaa' }}>
        * Test catalog is fetched from the backend and may take a moment to load.
      </div>
    </div>
  );
}

export default TestCatalog;