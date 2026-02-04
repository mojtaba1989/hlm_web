export const sensorStyles = {
  container: {
    display: "flex",
    flexDirection: "column",
    height: "100%", // Fills the quadrant
    width: "100%",
    background: "transparent",
  },
  controlPanel: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    padding: "8px 12px",
    borderBottom: "1px solid #2a2a2a",
    background: "#222",
    flexShrink: 0,
  },
  checkboxGroup: {
    display: "flex",
    flexWrap: "wrap",
    gap: "10px",
  },
  label: (isActive) => ({
    display: "flex",
    alignItems: "center",
    gap: 6,
    cursor: "pointer",
    fontSize: "11px",
    fontWeight: "600",
    color: isActive ? "#eee" : "#555",
    transition: "color 0.2s",
  }),
  checkbox: {
    cursor: "pointer",
    accentColor: "#0984e3",
  },
  actionGroup: {
    display: "flex",
    gap: 6,
  },
  miniBtn: {
    padding: "2px 8px",
    fontSize: "10px",
    background: "#333",
    color: "#ccc",
    border: "1px solid #444",
    borderRadius: "4px",
    cursor: "pointer",
    fontWeight: "bold",
  },
  chartWrapper: {
    flex: 1, // This is the secret—it takes up all remaining vertical space
    width: "100%",
    minHeight: 0, // Prevents chart from expanding the parent
    padding: "10px",
  },
};