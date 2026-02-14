import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { PopupTriggerProvider } from "./components/PopupTriggerContext";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <PopupTriggerProvider>
      <App />
    </PopupTriggerProvider>
  </React.StrictMode>,
);
