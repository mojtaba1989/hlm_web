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
    margin: "30px auto",
    padding: "0 20px",
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