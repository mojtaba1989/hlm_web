import { use, useEffect, useState } from "react";
// import { CONFIG as DEFAULT_CONFIG } from "./config_files/config";
import { configStyles } from "./styles/config_style";
import { useNavigate } from "react-router-dom";

const DEFAULT_CONFIG = {};
const backendUrl = import.meta.env.VITE_BACKEND_URL;

async function fetchConfig() {
  const res = await fetch(`${backendUrl}/api/config`);
  return res.json();
}

async function fetchDefaultConfig() {
  const res = await fetch(`${backendUrl}/api/default`);
  return res.json();
}

async function saveConfigApi(cfg) {
  return fetch(`${backendUrl}/api/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cfg),
  });
}

async function check_unsaved(cfg) {
  return fetch(`${backendUrl}/api/check_unsaved`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cfg),
  });
}

async function get_cameras() {
  return fetch(`${backendUrl}/api/camera_feed/cameras`)
  .then((res) => res.json());
}

async function get_ssids() {
  return fetch(`${backendUrl}/api/lights`)
  .then((res) => res.json());
}

/* =========================
   Input renderers
========================= */
function BooleanSelect({ value, disabled, onChange }) {
  return (
    <select
      value={String(value)}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value === "true")}
      style={configStyles.select}
    >
      <option value="true">TRUE</option>
      <option value="false">FALSE</option>
    </select>
  );
}

function TextInput({ value, disabled, onChange }) {
  return (
    <input
      value={value}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
      style={{
        ...configStyles.input,
        opacity: disabled ? 0.45 : 1,
      }}
    />
  );
}

function CameraInput({ value, disabled, onChange, cameras }) {
  return (
    <select
      value={value ?? ""}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
      style={configStyles.select}
    >
      {cameras.map((cam) => (
        <option key={cam.id} value={cam.path}>
          {cam.name}
        </option>
      ))}
    </select>
  );
}


/* =========================
   Field renderer
========================= */
function ConfigField({
  section,
  field,
  value,
  editable,
  enabled,
  onUpdate,
  cameras
}) {
  if (!editable) {
    return <span style={configStyles.readonly}>{String(value)}</span>;
  }

  if (typeof value === "boolean") {
    return (
      <BooleanSelect
        value={value}
        disabled={!enabled}
        onChange={(v) => onUpdate(section, field, v)}
      />
    );
  }

  if (field === "DEVICE_ID") {
    return (
      <CameraInput
        value={value}
        disabled={!enabled}
        onChange={(v) => onUpdate(section, field, v)}
        cameras={cameras}
      />
    );
  }

  return (
    <TextInput
      value={Array.isArray(value) ? value.join(", ") : value}
      disabled={!enabled}
      onChange={(v) =>
        onUpdate(
          section,
          field,
          Array.isArray(value)
            ? v.split(",").map((x) => Number(x.trim()))
            : typeof value === "number"
            ? Number(v)
            : v
        )
      }
    />
  );
}

/* =========================
   Section renderer
========================= */
function ConfigSection({ name, data, onUpdate, cameras}) {
  const enabled = data.ENABLED?.[0] ?? true;
  if (name === "Wifi") {
    return (
      WifiConfigSection({ name, data, onUpdate }));
  }

  return (
    <div
      style={{
        ...configStyles.section,
        backgroundColor: enabled ? "white" :  "#f2f2f2",
      }}
    >
      <h2 style={{...configStyles.sectionTitle, color: enabled ? "black" : "gray"}}>{name}</h2>

      {Object.entries(data).map(([key, val]) => {
        if (Array.isArray(val)) {
          const [value, editable] = val;
          return (
            <div key={key} style={configStyles.row}>
              <label style={configStyles.label}>{key}</label>
              <ConfigField
                section={name}
                field={key}
                value={value}
                editable={editable}
                enabled={key === "ENABLED" ? true : enabled}
                onUpdate={onUpdate}
                cameras={cameras}
              />
            </div>
          );
        }

        // nested (Channel_map)
        return (
          <div key={key} style={configStyles.section}>
            <div style={{...configStyles.subTitle, color: enabled ? "black" : "gray"}}>{key}</div>
            {Object.entries(val).map(([subKey, subVal]) => {
              const [value, editable] = subVal;
              return (
                <div key={subKey} style={configStyles.row}>
                  <label style={configStyles.label}>{subKey}</label>
                  {editable ? (
                    <TextInput
                      value={value}
                      disabled={!enabled}
                      onChange={(v) =>
                        onUpdate(name, key, v, subKey)
                      }
                    />
                  ) : (
                    <span style={configStyles.readonly}>{value}</span>
                  )}
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

function WifiConfigSection({ name, data, onUpdate }) {
  const [connect, setConnect] = useState(false);
  const [status, setStatus] = useState("○ OFFLINE");
  const [warn, setWarn] = useState(true);
  const enabled = data.ENABLED?.[0] ?? true;
  if (name !== "Wifi") {
      return (
        <div> </div>);
    }

  const handleWifiConnect = async() => {
    if (!connect) {
      setConnect(true);
      setStatus("● ONLINE");
    } else {
      setConnect(false);
      setStatus("○ OFFLINE");
    }
  };

  return (
    <div
      style={{
        ...configStyles.section,
        backgroundColor: enabled ? "white" :  "#f2f2f2",
      }}>
      
      <header style={{...configStyles.sectionTitle, display: "flex", justifyContent: "space-between", alignItems: "center"}}>
        <div>
          <h2 style={{...configStyles.sectionTitle, color: enabled ? "black" : "gray"}}>{name}</h2>
        </div>
        <div>
          <span style={configStyles.connectIndicator(connect, warn)}>{status}</span>
          <span> </span>
          <button style={configStyles.connectBtn(connect, "#27ae60")}
            onClick={handleWifiConnect}>
            {connect ? "Disconnect" : "Connect"}
          </button>
        </div>
      </header>
      
      {Object.entries(data).map(([key, val]) => {
        const [value, editable] = val;
        return (
          <div key={key} style={configStyles.row}>
            <label style={configStyles.label}>{key}</label>
            <ConfigField
              section={name}
              field={key}
              value={value}
              editable={editable}
              enabled={key === "ENABLED" ? true : enabled}
              onUpdate={onUpdate}
              cameras={[]}
            />
          </div>
        );
      })}
    </div>
  );
};
  

/* =========================
   Main Page
========================= */
export default function ConfigPage() {
  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [status, setStatus] = useState(null);
  const [cameras, setCameras] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    get_cameras()
      .then((data) => setCameras(data.cameras))
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchConfig()
      .then((cfg) => Object.keys(cfg).length && setConfig(cfg))
      .catch(() => {});
  }, []);

  const updateValue = (section, key, value, subKey = null) => {
    setConfig((prev) => {
      const updated = structuredClone(prev);
      if (subKey) {
        updated[section][key][subKey][0] = value;
      } else {
        updated[section][key][0] = value;
      }
      return updated;
    });
  };

  const saveConfig = async () => {
    setStatus("Saving...");
    try {
      await saveConfigApi(config);
      setStatus("✅ Saved");
    } catch {
      setStatus("❌ Save failed");
    }
  };

  const load_default = async() => {
    setStatus("Loading default config...");
    fetchDefaultConfig()
      .then((cfg) => Object.keys(cfg).length && setConfig(cfg))
      .catch(() => {});
    setStatus("Restored default config");
  };

  const handleBack = () => {
    check_unsaved(config)
      .then((res) => res.json())
      .then((data) => {
        if (data.unsaved) {
          if (window.confirm("You have unsaved changes, are you sure you want to leave?")) {
            navigate("/");
          }
        } else {
          navigate("/");
        }
      })
  };

  return(
    <div style={configStyles.page}>
      <header style={configStyles.header}>
        <div style={configStyles.headerLeft}>
          <button style={configStyles.backBtn} onClick={handleBack}>← Back</button>
          <h1 style={configStyles.title}>System Configuration</h1>
        </div>
        <div style={configStyles.headerActions}>
          <span style={configStyles.status}>{status}</span>
          <button onClick={load_default} style={configStyles.resetBtn}>Reset to Default</button>
          <button onClick={saveConfig} style={configStyles.saveBtn}>Save Changes</button>
        </div>
      </header>

      <main style={configStyles.container}>
        {Object.entries(config).map(([name, data]) => (
          <ConfigSection
            key={name}
            name={name}
            data={data}
            onUpdate={updateValue}
            cameras={cameras}
          />
        ))}
        {/* {Object.entries(config).map(([name, data]) => (
          <WifiConfigSection
            key={name}
            name={name}
            data={data}
            onUpdate={updateValue}
            cameras={cameras}
          />
        ))} */}
      </main>

      <footer style={configStyles.footer}>
        <span style={{ color: "#2f80ed", fontWeight: "800" }}>ACM</span>
        <span style={{ margin: "0 8px", color: "#ffffff" }}>|</span>
        <span style={{ color: "#ffffff" }}>
            Powered by <strong style={{ color: "#ffcc00", fontWeight: "700" }}>MTU</strong>
        </span>
        <span style={{ marginLeft: "8px", color: "#ffffff" }}>© 2026</span>
      </footer>
    </div>
  );
}
