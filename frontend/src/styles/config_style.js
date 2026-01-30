export const styles = {
  page: {
    padding: 24,
    background: "#f4f6f8",
    minHeight: "100vh",
    color: "#222", // ✅ FIX
    fontFamily: "Arial, sans-serif",
  },
  title: {
    marginBottom: 20,
    color: "#111",
  },
  section: {
    background: "#ffffff",
    padding: 16,
    borderRadius: 6,
    marginBottom: 16,
    boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
  },
  sectionTitle: {
    marginBottom: 12,
    color: "#333",
  },
  subSection: {
    marginTop: 12,
    paddingLeft: 10,
    borderLeft: "3px solid #ddd",
  },
  subTitle: {
    fontWeight: "bold",
    marginBottom: 6,
  },
  row: {
    display: "flex",
    alignItems: "center",
    marginBottom: 8,
  },
  label: {
    width: 180,
    fontWeight: 500,
    color: "#222",
  },
  input: {
    flex: 1,
    padding: "6px 8px",
    border: "1px solid #ccc",
    borderRadius: 4,
    color: "#111",
    background: "#fff",
  },
  select: {
    flex: 1,
    padding: "6px 8px",
    borderRadius: 4,
  },
  readonly: {
    flex: 1,
    color: "#777",
    fontStyle: "italic",
  },
  preview: {
    marginTop: 20,
    padding: 12,
    background: "#eaeaea",
    borderRadius: 4,
    fontSize: 12,
    color: "#111",
  },
  overlay: {
    position: "fixed",
    inset: 0,
    backgroundColor: "rgba(0,0,0,0.45)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  },
  popup: {
    backgroundColor: "#fff",
    padding: "20px",
    borderRadius: "8px",
    minWidth: "300px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
  },

  title: {
    margin: "0 0 10px 0",
    fontSize: "18px",
    fontWeight: 600,
  },

  message: {
    marginBottom: "20px",
    fontSize: "14px",
    color: "#444",
  },

  actions: {
    display: "flex",
    justifyContent: "flex-end",
    gap: "10px",
  },

  yesButton: {
    padding: "6px 14px",
    borderRadius: "6px",
    border: "none",
    cursor: "pointer",
    backgroundColor: "#d32f2f",
    color: "#fff",
    fontWeight: 500,
  },

  noButton: {
    padding: "6px 14px",
    borderRadius: "6px",
    border: "none",
    cursor: "pointer",
    backgroundColor: "#e0e0e0",
    color: "#333",
    fontWeight: 500,
  },
};