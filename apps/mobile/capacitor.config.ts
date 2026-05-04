import { CapacitorConfig } from "@capacitor/cli";

const serverUrl = process.env.PFL_WEB_URL || "http://localhost:8501";

const config: CapacitorConfig = {
  appId: "com.promptfaber.lab",
  appName: "Prompt Faber Lab",
  webDir: "www",
  server: {
    url: serverUrl,
    cleartext: true
  }
};

export default config;

