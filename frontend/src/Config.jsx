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
  return fetch(`${backendUrl}/api/wifi_ssids`)
  .then((res) => res.json());
}

async function connect_wifi(ssid, password, dev) {
  return fetch(`${backendUrl}/api/connect_wifi`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ssid, password, dev }),
  }).then((res) => res.json());
}

async function disconnect_wifi(dev) {
  return fetch(`${backendUrl}/api/disconnect_wifi`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dev }),
  }).then((res) => res.json());
}

async function wifi_status(dev) {
  return fetch(`${backendUrl}/api/wifi_status`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dev }),
  }).then((res) => res.json());
}

async function radio_on() {
  return fetch(`${backendUrl}/api/wifi_on`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  }).then((res) => res.json());
}

async function radio_off() {
  return fetch(`${backendUrl}/api/wifi_off`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  }).then((res) => res.json());
}

async function wifi_devices() {
  return fetch(`${backendUrl}/api/wifi_devices`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  }).then((res) => res.json());
}

async function get_wifi_ip(dev) {
  return fetch(`${backendUrl}/api/wifi_ip`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dev }),
  }).then((res) => res.json());
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

function CameraInput({ value, disabled, onChange }) {
  const [isScanning, setIsScanning] = useState(false);
  const [cameras, setCameras] = useState([]);
  const [initialized, setInitialized] = useState(false);
  
  useEffect(() => {
    if (!initialized) {
      get_cameras().then((data) => {
        setCameras(data.cameras);
        setInitialized(true);
      });
    }
  }, [initialized]);

  return (
    <div>
      <select
        value={value ?? ""}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        style={configStyles.select}
      >
        <option value="" disabled>-- Select Camera --</option>
        {Array.isArray(cameras) && cameras.length > 0 ? (
          cameras.map((cam, index) => (
            <option key={index} value={cam.path} style={{ color: "#000", background: "#fff" }}>
              {cam.name}
            </option>
          ))
        ) : (
          <option value="" disabled>No Cameras Found</option>
        )}
      </select>
      <button
        disabled={disabled || isScanning}
        onClick={() => {
          setIsScanning(true);
          get_cameras().then((data) => {
            setCameras(data.cameras);
            setIsScanning(false);
          }).catch(() => setIsScanning(false));
        }}
        style={configStyles.refreshBtn(!disabled, isScanning)}
        title="Scan for camera devices"
      >
        <span>↻</span>
      </button>
    </div>
  );
}

function SSIDInput({ value, disabled, onChange}) {
  const [isScanning, setIsScanning] = useState(false);
  const [ssids, setSsids] = useState([]);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (!initialized) {
      get_ssids().then((res) => {
        if (res.status === "success") {
          setSsids(res.ssids);
        }
        setInitialized(true);
      });
    }
  }, [initialized]);

  return (
    <div>
      <select
        value={value ?? ""}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        style={configStyles.select}
      >
        <option value="" disabled>-- Select WiFi Network --</option>
        {Array.isArray(ssids) && ssids.length > 0 ? (
          ssids.map((ssid, index) => (
            <option key={index} value={ssid} style={{ color: "#000", background: "#fff" }}>
              {ssid}
            </option>
          ))
        ) : (
          <option value="" disabled>No SSIDs Found</option>
        )}
      </select>
      <button
        disabled={disabled}
        onClick={() => {
          setIsScanning(true);
          get_ssids().then((res) => {
            if (res.status === "success") {
              setSsids(res.ssids);
            }
            setIsScanning(false);
          }).catch(() => setIsScanning(false));
        }}
        style={configStyles.refreshBtn(!disabled, isScanning)}
        title="Scan for WiFi networks"
      >
        <span>↻</span>
      </button>
    </div>
  );
}

function WifiDeviceSelect({ value, disabled, onChange }) {
  const [isScanning, setIsScanning] = useState(false);
  const [wifiDevices, setWifiDevices] = useState([]);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (!initialized) {
      wifi_devices().then((res) => {
        if (res.status === "success") {
          setWifiDevices(res.devices);
        }
        setInitialized(true);
      });
    }
  }, [initialized]);

  return (
    <div>
      <select
        value={value ?? ""}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        style={configStyles.select}
      >
        <option value="" disabled>-- Select WiFi Device --</option>
        {Array.isArray(wifiDevices) && wifiDevices.length > 0 ? (
          wifiDevices.map((dev, index) => (
            <option key={index} value={dev} style={{ color: "#000", background: "#fff" }}>
              {dev}
            </option>
          ))
        ) : (
          <option value="" disabled>No WiFi Devices Found</option>
        )}
      </select>
      <button
        disabled={disabled || isScanning}
        onClick={() => {
          setIsScanning(true);
          wifi_devices().then((res) => {
            if (res.status === "success") {
              setWifiDevices(res.devices);
            }
            setIsScanning(false);
          }).catch(() => setIsScanning(false));
        }}
        style={configStyles.refreshBtn(!disabled, isScanning)}
        title="Scan for WiFi devices"
      >
        <span>↻</span>
      </button>
    </div>
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
      />
    );
  }

  if (field === "SSID") {
    return (
      <SSIDInput
        value={value}
        disabled={!enabled}
        onChange={(v) => onUpdate(section, field, v)}
      />
    );
  }

  if (field === "INTERFACE") {
    return (
      <WifiDeviceSelect
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
function ConfigSection({ name, data, onUpdate}) {
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
  const [statusChecked, setStatusChecked] = useState(false);

  useEffect(() => {
    console.log(data.DHCP?.[0], data.DHCP?.[1])
    if (data.DHCP?.[0]){
      get_wifi_ip(data.INTERFACE[0]).then((res) => {
        console.log("IP fetch result:", res.ip_addresses);
        if (res.status === "success") {
          data.MANUAL_IP[0] = res.ip_addresses;
          data.MANUAL_IP[1] = false;
        } else {
          data.MANUAL_IP[1] = true;
        }
      });
    }
  }, [data.DHCP?.[0], data.INTERFACE, statusChecked]);
  
  useEffect(() => {
    if (enabled && connect) {
    } else if (enabled && !connect) {
      radio_on();
    } else {
      radio_off();
      setConnect(false);
      setStatus("○ OFFLINE");
    }
  }, [enabled]);

  useEffect(() => {
    if (!statusChecked) {
      wifi_status(data.INTERFACE[0]).then((res) => {
        if (res.status === "success") {
          if (res.device_state === "connected") {
            setStatus("● ONLINE");
            setWarn(false);
            setConnect(true);
          } else {
            setStatus("○ OFFLINE");
            setWarn(true);
            setConnect(false);
          }
        } else {
          setStatus("○ OFFLINE");
          setWarn(true);
          setConnect(false);
        }
      }).catch(() => {
        setStatus("○ OFFLINE");
        setWarn(true);
        setConnect(false);
      });
    }
    setStatusChecked(true);
  }, []);

  const handleWifiConnect = async() => {
    if (!connect) {
      connect_wifi(data.SSID[0], data.PASSWORD[0], data.INTERFACE[0])
        .then((res) => {
          if (res.status === "success") {
            setConnect(true);
            setStatus("● ONLINE");
            setWarn(false);
          } else {
            setWarn(true);
            alert("Failed to connect to WiFi: " + res.message);
          }
        })
        .catch((err) => {
          setWarn(true);
          alert("Error connecting to WiFi: " + err.message);
        });
    } else {
      disconnect_wifi(data.INTERFACE[0])
        .then((res) => {
          if (res.status === "success") {
            setConnect(false);
            setStatus("○ OFFLINE");
            setWarn(false);  
          } else {
            alert("Failed to disconnect WiFi: " + res.message);
          }
        })
        .catch((err) => {
          alert("Error disconnecting WiFi: " + err.message);
        });
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
          <button style={configStyles.connectBtn(connect, enabled)}
            onClick={handleWifiConnect}
            disabled={!enabled}>
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
  const navigate = useNavigate();

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

      <div style={configStyles.container}>
          {Object.entries(config).map(([name, data]) => (
            <ConfigSection
              key={name}
              name={name}
              data={data}
              onUpdate={updateValue}
            />
          ))}
      </div>

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
