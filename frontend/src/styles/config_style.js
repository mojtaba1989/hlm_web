export const configStyles = {
  page: {
    height: "100vh",      // Lock to exactly screen height
    width: "100%",       // Lock to exactly screen width
    // display: "flex",
    // flexDirection: "column",
    overflow: "auto",   // Disables global scrollbars
    background: "#0f0f0f", // Slightly darker for better contrast
    color: "#e0e0e0",
    fontFamily: "'Inter', -apple-system, sans-serif",
  },
  header: {
    height: "60px",       // Fixed height
    flexShrink: 0,        // Prevents header from collapsing
    background: "#1a1a1a",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0 20px",
    borderBottom: "1px solid #333",
    boxShadow: "0 2px 10px rgba(0,0,0,0.5)",
  },
  headerLeft: { display: "flex", alignItems: "center", gap: "20px" },
  title: { fontSize: "20px", fontWeight: "700", margin: 0 },
  
  container: {
    maxWidth: "900px",
    maxHeight: "85%",
    margin: "10px auto",
    padding: "0 20px",
    overflowY: "auto",
    flex: 1,
  },

  // Button Improvements
  saveBtn: {
    padding: "10px 20px",
    backgroundColor: "#0984e3", // Vibrant Blue
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "background 0.2s",
    fontSize: "16px",
    "&:hover": {
      backgroundColor: "#b3006e",
    }
  },
  resetBtn: {
    padding: "10px 20px",
    backgroundColor: "#3acabe", // Vibrant Blue
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "background 0.2s",
    fontSize: "16px",
    marginRight: "20px",
  },
  backBtn: {
    background: "none",
    border: "none",
    color: "#0984e3",
    cursor: "pointer",
    fontSize: "20px",
    fontWeight: "600",
  },

  connectBtn: (active, enabled) => ({
    backgroundColor: enabled ?  (active ? "#b22222" : "#27ae60") : "#ccc",
    color: "white",
    border: "none",
    padding: "8px 14px",
    borderRadius: "5px",
    fontSize: "16px",
    fontWeight: "700",
    cursor: enabled ? "pointer" : "not-allowed",
    transition: "all 0.2s ease",
  }),

  connectIndicator: (active, warn) => ({
    fontSize: "10px",
    fontWeight: "bold",
    color: active ? (warn ? "#e6b959" : "#27ae60") : "#57606f",
    padding: "2px 8px",
    borderRadius: "10px",
    border: `1px solid ${active ? (warn ? "#e6b959" : "#27ae60") : "#333"}`,
  }),
  refreshBtn: (active, isRefreshing) => ({
    marginLeft: "10px",
    padding: "6px 10px",
    fontSize: "20px",
    fontWeight: "600", // Icons look better slightly larger
    cursor: isRefreshing ? "not-allowed" : "pointer",
    background: "transparent",
    border: "1px solid #dfe6e9",
    borderRadius: "4px",
    alignItems: "center",
    justifyContent: "center",
    color: active ? (isRefreshing ? "#ccc" : "#0984e3") : "#ccc",
    transition: "all 0.2s",
  }),
  // Section/Card Styling
  section: {
    background: "#ffffff",
    padding: "24px",
    borderRadius: "12px",
    marginBottom: "20px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
    border: "1px solid #edf2f7",
    fontSize: "16px",
    // color: "#333",
  },
  row: {
    display: "flex",
    alignItems: "center",
    paddingVertical: "12px",
    borderBottom: "1px solid #f1f2f6",
    marginBottom: "12px",
  },
  select: {
    padding: "10px 12px",
    border: "1px solid #dfe6e9",
    borderRadius: "6px",
    fontSize: "14px",
    outline: "none",
    transition: "border-color 0.2s",
  },
  label: {
    flex: "0 0 240px",
    fontSize: "14px",
    fontWeight: "600",
    color: "#636e72",
  },
  input: {
    flex: 1,
    padding: "10px 12px",
    border: "1px solid #dfe6e9",
    borderRadius: "6px",
    fontSize: "14px",
    outline: "none",
    transition: "border-color 0.2s",
    "&:focus": { borderColor: "#0984e3" }
  },
  status: {
    marginRight: "15px",
    fontSize: "13px",
    color: "#00b894", // Success green
    fontWeight: "500"
  },
  footer: {
    height: "30px",
    flexShrink: 0,
    background: "#0f0f0f",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "11px",
    color: "#444",
    gap: "10px",
    borderTop: "1px solid #222",
  }
};