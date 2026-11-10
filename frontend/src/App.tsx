import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8001";

function App() {
  const [status, setStatus] = useState("checking...");

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => res.json())
      .then((data) => setStatus(data.status))
      .catch((err) => setStatus(`error: ${err.message}`));
  }, []);

  return (
    <main>
      <h1>Mini 360</h1>
      <p>Backend health: {status}</p>
    </main>
  );
}

export default App;
