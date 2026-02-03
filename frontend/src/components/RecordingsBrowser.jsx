import { useEffect, useState, useMemo } from "react";
import { styles } from "../styles/config_style";

function FolderBrowser() {
  const [path, setPath] = useState("");
  const [folders, setFolders] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  useEffect(() => {
    fetch(`${backendUrl}/api/records/list?subpath=${encodeURIComponent(path)}`)
      .then((res) => res.json())
      .then((data) => {
        setFolders(data.folders || []);
        setSelected(new Set()); 
      })
      .catch((err) => console.error("Fetch error:", err));
  }, [path, backendUrl]);

  const groupedFolders = useMemo(() => {
    const getGroupName = (name) => {
      try {
        const year = name.substring(0, 4);
        const month = name.substring(4, 6);
        const day = name.substring(6, 8);
        const folderDate = new Date(`${year}-${month}-${day}T00:00:00`);
        
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const lastWeek = new Date(today);
        lastWeek.setDate(lastWeek.getDate() - 7);

        if (isNaN(folderDate.getTime())) return "Older";
        if (folderDate >= today) return "Today";
        if (folderDate >= yesterday) return "Yesterday";
        if (folderDate >= lastWeek) return "Last Week";
        return "Older";
      } catch {
        return "Older";
      }
    };

    const groups = { Today: [], Yesterday: [], "Last Week": [], Older: [] };
    folders.forEach(f => groups[getGroupName(f.name)].push(f));
    return groups;
  }, [folders]);

  const toggleSelect = (name) => {
    const fullPath = path ? `${path}/${name}` : name;
    const newSet = new Set(selected);
    if (newSet.has(fullPath)) newSet.delete(fullPath);
    else newSet.add(fullPath);
    setSelected(newSet);
  };

  const toggleGroup = (groupItems) => {
    const newSet = new Set(selected);
    const itemPaths = groupItems.map(f => path ? `${path}/${f.name}` : f.name);
    const allInGroupSelected = itemPaths.every(p => selected.has(p));

    itemPaths.forEach(p => {
      if (allInGroupSelected) newSet.delete(p);
      else newSet.add(p);
    });
    setSelected(newSet);
  };

  const downloadSelected = () => {
    if (selected.size === 0) return;
    const params = new URLSearchParams();
    selected.forEach(p => params.append("paths", p));
    window.location.href = `${backendUrl}/api/records/download-multiple?${params.toString()}`;
  };

  return (
    <div style={{ width: "100%", padding: "20px", boxSizing: "border-box", fontFamily: "sans-serif" }}>
      
      {/* Header Bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", flexWrap: "wrap", gap: "10px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
          <h2 style={{ margin: 0 }}>Path: /{path}</h2>
          {path && (
            <button onClick={() => setPath(path.split("/").slice(0, -1).join("/"))} style={{ padding: "6px 12px" }}>
              ← Up
            </button>
          )}
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          {selected.size > 0 && (
            <button onClick={() => setSelected(new Set())} style={{ background: "#fff", border: "1px solid #ccc", padding: "8px 15px" }}>
              Clear All
            </button>
          )}
          <button 
            onClick={downloadSelected} 
            disabled={selected.size === 0}
            style={{ padding: "8px 20px", fontWeight: "bold", backgroundColor: selected.size > 0 ? "#007bff" : "#ccc", color: "white", border: "none", borderRadius: "4px" }}
          >
            Download ({selected.size})
          </button>
        </div>
      </div>

      {/* Table Headings */}
      <div style={{ display: "flex", padding: "12px", background: "#f1f3f5", borderBottom: "2px solid #dee2e6", fontWeight: "bold" }}>
        <div style={{ width: "40px" }}></div>
        <div style={{ flex: "2" }}>Folder Name</div>
        <div style={{ flex: "1" }}>Duration</div>
        <div style={{ width: "150px", textAlign: "right" }}>Actions</div>
      </div>

      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {Object.entries(groupedFolders).map(([groupName, items]) => {
          if (items.length === 0) return null;

          const groupPaths = items.map(f => path ? `${path}/${f.name}` : f.name);
          const isGroupSelected = groupPaths.every(p => selected.has(p));

          return (
            <div key={groupName}>
              {/* Category Header */}
              <div style={{ display: "flex", alignItems: "center", padding: "10px", background: "#e9ecef", borderBottom: "1px solid #ced4da" }}>
                <input 
                  type="checkbox" 
                  checked={isGroupSelected} 
                  onChange={() => toggleGroup(items)}
                  style={{ width: "18px", height: "18px" }}
                />
                <span style={{ marginLeft: "12px", fontWeight: "bold", textTransform: "uppercase", fontSize: "0.85rem", color: "#495057" }}>
                  {groupName} <span style={{ fontWeight: "normal", opacity: 0.6 }}>— {items.length} folders</span>
                </span>
              </div>

              {/* Folder Rows */}
              {items.map((folder) => {
                const fullPath = path ? `${path}/${folder.name}` : folder.name;
                const isChecked = selected.has(fullPath);

                return (
                  <li 
                    key={folder.name} 
                    style={{ 
                      display: "flex", 
                      alignItems: "center", 
                      padding: "12px", 
                      borderBottom: "1px solid #eee",
                      backgroundColor: isChecked ? "#f8fbff" : "#fff"
                    }}
                  >
                    <div style={{ width: "40px" }}>
                      <input 
                        type="checkbox" 
                        checked={isChecked} 
                        onChange={() => toggleSelect(folder.name)}
                        style={{ width: "16px", height: "16px" }}
                      />
                    </div>
                    
                    <div style={{ flex: "2", display: "flex", alignItems: "center", gap: "8px" }}>
                       <span style={{ fontSize: "1.2rem" }}>📁</span> {folder.name}
                    </div>
                    
                    <div style={{ flex: "1", color: "#666" }}>
                      {folder.duration || "--:--"}
                    </div>

                    <div style={{ width: "150px", display: "flex", gap: "8px", justifyContent: "flex-end" }}>
                      <button onClick={() => setPath(fullPath)} style={{ padding: "4px 8px" }}>Open</button>
                      <a href={`${backendUrl}/api/records/download-folder?path=${encodeURIComponent(fullPath)}`}>
                        <button style={{ padding: "4px 8px" }}>Zip</button>
                      </a>
                    </div>
                  </li>
                );
              })}
            </div>
          );
        })}
      </ul>
    </div>
  );
}

export default FolderBrowser;