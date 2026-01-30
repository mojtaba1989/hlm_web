import { use, useEffect, useState } from "react";
// import { CONFIG as DEFAULT_CONFIG } from "./config_files/config";
import { styles } from "./styles/config_style";
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

/* =========================
   Input renderers
========================= */
function BooleanSelect({ value, disabled, onChange }) {
  return (
    <select
      value={String(value)}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value === "true")}
      style={styles.select}
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
        ...styles.input,
        opacity: disabled ? 0.45 : 1,
      }}
    />
  );
}

function CameraInput({value, disabled, onChange, cameras}) {
  return (
    <select
      value={value}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
      style={styles.select}
    >
      {cameras.length === 0 ? (
          <option>Loading cameras...</option>
        ) : (
          cameras.map(([path, name]) => (
            <option key={path} value={path}>
              {name}
            </option>
          ))
        )}
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
    return <span style={styles.readonly}>{String(value)}</span>;
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

  if (field === "Devide_ID"){
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

  return (
    <div
      style={{
        ...styles.section,
        // opacity: enabled ? 1 : 0.45,
      }}
    >
      <h2 style={styles.sectionTitle}>{name}</h2>

      {Object.entries(data).map(([key, val]) => {
        if (Array.isArray(val)) {
          const [value, editable] = val;
          return (
            <div key={key} style={styles.row}>
              <label style={styles.label}>{key}</label>
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
          <div key={key} style={styles.subSection}>
            <div style={styles.subTitle}>{key}</div>
            {Object.entries(val).map(([subKey, subVal]) => {
              const [value, editable] = subVal;
              return (
                <div key={subKey} style={styles.row}>
                  <label style={styles.label}>{subKey}</label>
                  {editable ? (
                    <TextInput
                      value={value}
                      disabled={!enabled}
                      onChange={(v) =>
                        onUpdate(name, key, v, subKey)
                      }
                    />
                  ) : (
                    <span style={styles.readonly}>{value}</span>
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

  return (
    <div style={styles.page}>
      <button onClick={() => {
        check_unsaved(config).
          then(res => res.json()).
          then(data => {
            console.log(data.unsaved);
            if (data.unsaved){
              if (confirm("You have unsaved changes. Are you sure you want to leave?")){
                navigate("/")
              }
            } else {
              navigate("/");
            }
          });
        }}>Back</button>
      <h1 style={styles.title}>System Configuration</h1>

      <button onClick={saveConfig} style={styles.saveBtn}>
        Save
      </button>

      <button
        onClick={load_default} style={styles.resetBtn}
      >
        Reset
      </button>

      <span style={styles.status}>{status}</span>

      {Object.entries(config).map(([name, data]) => (
        <ConfigSection
          key={name}
          name={name}
          data={data}
          onUpdate={updateValue}
          cameras={cameras}
        />
      ))}
    </div>
  );
}
