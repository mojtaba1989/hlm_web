import { useEffect, useState } from "react";
import { homeStyles } from "../styles/home_style";

function TestCatalog() {
  const [testCatalog, setTestCatalog] = useState([]);
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  useEffect(() => {
    fetch(`${backendUrl}/api/test_catalog`, { method: "GET" }).
    then(res => res.json()).
    then(data => setTestCatalog(data.scenarios)).
    catch(err => console.error("Failed to fetch test catalog:", err));
    }, []);
    
    return (
      <div style={{ display: 'flex',
                    flexDirection: 'column', 
                    alignItems: 'left',
                    marginLeft: '20px',
                    marginRight: '10px',
      }}>
        <p style={{ fontWeight: 'bold', color: '#888' }}>Test Catalog</p>
        <select 
          onChange={(e) => console.log(e.target.value)} 
          style={{ padding: '8px', borderRadius: '4px' }}
        >
          <option value="">Select a test...</option>
          {Array.isArray(testCatalog) && testCatalog.map((desc, index) => (
            <option key={index} value={desc}>
              {desc}
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