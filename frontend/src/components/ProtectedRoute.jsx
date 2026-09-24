import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

const API = "http://localhost:8000";

function ProtectedRoute({ children, adminOnly = false }) {
  const [status, setStatus] = useState("checking"); // checking | ok | denied

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setStatus("denied");
      return;
    }

    // Verify the token is real by calling an endpoint that requires it.
    // admin-only routes verify against an admin-only endpoint.
    const verifyUrl = adminOnly ? `${API}/admin/users` : `${API}/new-session`;
    const options = adminOnly
      ? { headers: { Authorization: `Bearer ${token}` } }
      : { method: "POST", headers: { Authorization: `Bearer ${token}` } };

    fetch(verifyUrl, options)
      .then((res) => {
        if (res.status === 401 || res.status === 403) {
          localStorage.clear();
          setStatus("denied");
        } else {
          setStatus("ok");
        }
      })
      .catch(() => setStatus("denied"));
  }, [adminOnly]);

  if (status === "checking") return null; // or a loading spinner
  if (status === "denied") return <Navigate to="/login" replace />;

  return children;
}

export default ProtectedRoute;