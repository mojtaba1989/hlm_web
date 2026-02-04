export const homeStyles = {
  // 1. MAIN PAGE SHELL
  page: {
    height: "100vh",      // Lock to exactly screen height
    width: "100%",       // Lock to exactly screen width
    display: "flex",
    flexDirection: "column",
    overflow: "auto",   // Disables global scrollbars
    background: "#0f0f0f", // Slightly darker for better contrast
    color: "#e0e0e0",
    fontFamily: "'Inter', -apple-system, sans-serif",
  },

  // 2. STABLE HEADER
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

  brand: {
    display: "flex",
    alignItems: "center",
    gap: "15px",
  },

  // 3. FULL-WINDOW GRID
  grid: {
    flex: 1,              // Grows to fill exactly the remaining space
    display: "grid",
    minHeight: 0,         // IMPORTANT: Allows grid content to shrink below its natural size
    padding: "12px",
    gap: "12px",
    gridTemplateColumns: "1fr 1fr", 
    gridTemplateRows: "1fr 1fr",    // Splits remaining space 50/50
    gridTemplateAreas: `
      "video test"
      "sensors logs"
    `,
  },

  // 4. QUADRANT PANELS
  panel: {
    background: "#181818",
    borderRadius: "8px",
    border: "1px solid #2a2a2a",
    display: "flex",
    flexDirection: "column",
    minHeight: 0,         // IMPORTANT: Necessary for internal scrolling
    overflow: "hidden",
  },

  panelHeader: {
    padding: "10px 14px",
    background: "#222",
    fontSize: "11px",
    fontWeight: "700",
    color: "#888",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    borderBottom: "1px solid #2a2a2a",
    flexShrink: 0,
  },

  // 5. CAMERA VIEWPORT (Top-Left)
  viewport: {
    flex: 1,
    background: "#000",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden", // Ensures video doesn't "push" the panel size
  },

  videoWrapper: {
    width: "100%",
    height: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },

  // 6. INTERNAL SCROLLABLE AREAS (Bottom Panels)
  scrollArea: {
    flex: 1,
    overflowY: "auto",
    padding: "15px",
    scrollbarWidth: "thin",
    scrollbarColor: "#444 transparent",
  },

  // 7. PLACEHOLDER (Top-Right)
  placeholder: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    border: "1px dashed #333",
    margin: "15px",
    borderRadius: "6px",
    color: "#555",
    backgroundColor: "rgba(255,255,255,0.02)",
  },

  // 8. INTERACTIVE BUTTONS
  buttonGroup: {
    display: "flex",
    gap: "10px",
  },

  actionBtn: (active, baseColor) => ({
    backgroundColor: active ? "#b22222" : baseColor,
    color: "white",
    border: "none",
    padding: "8px 14px",
    borderRadius: "5px",
    fontSize: "16px",
    fontWeight: "700",
    cursor: "pointer",
    transition: "all 0.2s ease",
  }),

  navBtn: {
    backgroundColor: "#407880",
    color: "#fff",
    border: "1px solid #444",
    padding: "8px 14px",
    borderRadius: "5px",
    fontSize: "16px",
    fontWeight: "700",
    cursor: "pointer",
  },

  // 9. DYNAMIC LIVE INDICATOR
  liveIndicator: (active) => ({
    fontSize: "10px",
    fontWeight: "bold",
    color: active ? "#ff4757" : "#57606f",
    padding: "2px 8px",
    borderRadius: "10px",
    border: `1px solid ${active ? "#ff4757" : "#333"}`,
  }),

  // 10. FIXED FOOTER
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