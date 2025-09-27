/**
 * External dependencies.
 */
import React from "react";
import ReactDOM from "react-dom/client";

/**
 * Internal dependencies.
 */
import App from "./App";
import "./index.css";

function renderApp() {
  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}

// Check if boot data is already available (production scenario)
if (window.frappe?.boot) {
  renderApp();
} else if (import.meta.env.DEV) {
  // Development mode: fetch boot data via API
  fetch("/api/method/hms.boot.get_bootinfo", {
    method: "POST",
  })
    .then((response) => response.json())
    .then((values) => {
      const bootData = values.message;
      if (!window.frappe) window.frappe = {};
      window.frappe.boot = bootData;
      renderApp();
    })
    .catch((error) => {
      console.error("Failed to load boot data:", error);
      // Render app anyway if boot fails
      renderApp();
    });
} else {
  // Production fallback if boot data isn't embedded
  renderApp();
}
