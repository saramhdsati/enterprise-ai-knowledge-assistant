import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Login.css";

function Signup() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Signup failed");
      }

      setSuccess(true);
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setError(err.message === "Username already exists" ? "Username already exists" : "Signup failed. Try again.");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="login-icon">✓</div>
          <h2>Account created</h2>
          <p>An admin needs to assign you a department before you can start asking questions. Redirecting to sign in...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSignup}>
        <div className="login-icon">✦</div>
        <h2>Knowledge Assistant</h2>
        <p>Create your account</p>

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
        <input
          type="password"
          placeholder="Confirm password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />

        {error && <div className="login-error">{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Creating account..." : "Sign up"}
        </button>

        <p className="login-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </div>
  );
}

export default Signup;