import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Login.css";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const body = new URLSearchParams();
      body.append("username", username);
      body.append("password", password);

      const res = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      if (!res.ok) {
        throw new Error("Incorrect username or password");
      }

      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("role", data.role);
      localStorage.setItem("departments", JSON.stringify(data.departments));
      localStorage.setItem("username", username);

      navigate(data.role === "admin" ? "/admin" : "/chat");
    } catch (err) {
      setError("Incorrect username or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleLogin}>
        <div className="login-icon">✦</div>
        <h2>Knowledge Assistant</h2>
        <p>Sign in to continue</p>

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && <div className="login-error">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
                <p className="login-footer">
          Don't have an account? <Link to="/signup">Sign up</Link>
        </p>
      </form>
    </div>
  );
}

export default Login;