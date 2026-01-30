import { useEffect, useState } from "react";
import { CONFIG as DEFAULT_CONFIG } from "./config_files/config";
import { styles } from "./styles/config_style";

const backendUrl = import.meta.env.VITE_BACKEND_URL;
async function fetchConfig() {
  const res = await fetch(`${backendUrl}/api/config`);
  return res.json();
}

async function saveConfigApi(cfg) {
  return fetch(`${backendUrl}/api/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cfg),
  });
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
      <option value="true">true</option>
      <option value="false">false</option>
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
function ConfigSection({ name, data, onUpdate }) {
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
  const [status, setStatus] = useState("");

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

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>System Configuration</h1>

      <button onClick={saveConfig} style={styles.saveBtn}>
        Save
      </button>
      <span style={styles.status}>{status}</span>

      {Object.entries(config).map(([name, data]) => (
        <ConfigSection
          key={name}
          name={name}
          data={data}
          onUpdate={updateValue}
        />
      ))}
    </div>
  );
}
