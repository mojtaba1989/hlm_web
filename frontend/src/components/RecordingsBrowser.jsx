import { useEffect, useState } from "react";
import axios from "axios";

function FolderBrowser() {
  const [path, setPath] = useState("");
  const [folders, setFolders] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  useEffect(() => {
    fetch(`${backendUrl}/api/records/list?subpath=${encodeURIComponent(path)}`)
      .then(res => res.json())
      .then(data => {
        setFolders(data.folders);
        setSelected(new Set()); // clear selection when changing dir
      });
  }, [path]);

  const toggleSelect = (name) => {
    const fullPath = path ? `${path}/${name}` : name;
    const newSet = new Set(selected);

    if (newSet.has(fullPath)) {
      newSet.delete(fullPath);
    } else {
      newSet.add(fullPath);
    }

    setSelected(newSet);
  };

  const downloadSelected = () => {
    if (selected.size === 0) {
      alert("No folders selected");
      return;
    }

    const params = new URLSearchParams();
    selected.forEach(p => params.append("paths", p));

    window.location.href = `${backendUrl}/api/records/download-multiple?${params.toString()}`;
  };

  return (
    <div style={{ width: "600px" }}>
      <h3>Path: /{path}</h3>

      {path && (
        <button onClick={() => {
          const parts = path.split("/");
          parts.pop();
          setPath(parts.join("/"));
        }}>
          .. (up)
        </button>
      )}

      {/* Batch action bar */}
      <div style={{ margin: "10px 0" }}>
        <button
          onClick={downloadSelected}
          disabled={selected.size === 0}
        >
          Download Selected ({selected.size})
        </button>
      </div>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {folders.map(folder => {
          const fullPath = path ? `${path}/${folder.name}` : folder.name;
          const isChecked = selected.has(fullPath);

          return (
          <li
            key={folder.name}
            className="folder-row"
            >
            {/* Left: checkbox */}
            <input
                type="checkbox"
                checked={isChecked}
                onChange={() => toggleSelect(folder.name)}
            />

            {/* Middle: folder name */}
            <span className="folder-name">
                📁 {folder.name}
            </span>

            {/* Right: actions (hidden by default) */}
            <div className="folder-actions">
                <button onClick={() => setPath(fullPath)}>
                Open
                </button>

                <a
                href={`${backendUrl}/api/records/download-folder?path=${encodeURIComponent(fullPath)}`}
                >
                <button>
                    Zip
                </button>
                </a>
            </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default FolderBrowser;
