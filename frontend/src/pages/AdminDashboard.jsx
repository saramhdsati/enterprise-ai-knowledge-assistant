import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminDashboard.css";

const DEPARTMENTS = ["HR", "IT", "Company"];
const API = "http://localhost:8000";

function AdminDashboard() {
  const [tab, setTab] = useState("upload");
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const username = localStorage.getItem("username");
  const authHeader = { Authorization: `Bearer ${token}` };

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <div className="app">
      {/* Sidebar - same identity as chat */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">✦</div>
          <div>
            <h2>NovaBridge AI</h2>
            <span>Enterprise Knowledge</span>
          </div>
        </div>

        <button className="new-chat" onClick={() => navigate("/chat")}>
          <span>💬</span>
          Back to chat
        </button>

        <div className="sidebar-section">
          <p className="section-title">ADMIN</p>
          <button
            className={`conversation ${tab === "upload" ? "active" : ""}`}
            onClick={() => setTab("upload")}
          >
            <span>📄</span>Upload Documents
          </button>
          <button
            className={`conversation ${tab === "users" ? "active" : ""}`}
            onClick={() => setTab("users")}
          >
            <span>👥</span>Manage Users
          </button>
        </div>

        <div className="sidebar-bottom">
          <div className="user-avatar">{username?.[0]?.toUpperCase()}</div>
          <div className="user-info">
            <strong>{username}</strong>
            <span>Admin</span>
          </div>
          <button className="settings" onClick={handleLogout}>⎋</button>
        </div>
      </aside>

      {/* Main area */}
      <main className="chat-area">
        <header className="topbar">
          <div>
            <h1>Admin Dashboard</h1>
            <p>Manage documents and user access</p>
          </div>
          <div className="status">
            <span className="status-dot"></span>
            Online
          </div>
        </header>

        <section className="admin-content">
          {tab === "upload" ? (
            <UploadTab authHeader={authHeader} />
          ) : (
            <UsersTab authHeader={authHeader} />
          )}
        </section>
      </main>
    </div>
  );
}

function UploadTab({ authHeader }) {
  const [file, setFile] = useState(null);
  const [department, setDepartment] = useState(DEPARTMENTS[0]);
  const [status, setStatus] = useState("");
  const [documents, setDocuments] = useState([]);

  const loadDocuments = async () => {
    const res = await fetch(`${API}/admin/documents`, { headers: authHeader });
    if (res.ok) setDocuments(await res.json());
  };

  useEffect(() => { loadDocuments(); }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setStatus("Uploading...");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("department", department);

    try {
      const res = await fetch(`${API}/admin/upload`, {
        method: "POST",
        headers: authHeader,
        body: formData,
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setStatus(`✅ ${data.filename} uploaded — ${data.chunks_added} chunks (${data.department})`);
      setFile(null);
      loadDocuments();
    } catch {
      setStatus("⚠️ Upload failed.");
    }
  };

  return (
    <>
      <div className="panel-card">
        <h3>Upload a document</h3>
        <form className="upload-form" onSubmit={handleUpload}>
          <label className="file-input">
            <input type="file" onChange={(e) => setFile(e.target.files[0])} />
            <span>{file ? file.name : "Choose file..."}</span>
          </label>
          <select value={department} onChange={(e) => setDepartment(e.target.value)}>
            {DEPARTMENTS.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
          <button type="submit" className="primary-btn">Upload</button>
        </form>
        {status && <p className="status-msg">{status}</p>}
      </div>

      <div className="panel-card">
        <h3>Indexed documents</h3>
        <table className="admin-table">
          <thead>
            <tr><th>File</th><th>Department</th><th>Chunks</th></tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.filename}>
                <td>{doc.filename}</td>
                <td><span className="badge">{doc.department}</span></td>
                <td>{doc.chunk_count}</td>
              </tr>
            ))}
            {documents.length === 0 && (
              <tr><td colSpan={3} className="empty-row">No documents yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

function UsersTab({ authHeader }) {
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({ username: "", password: "", role: "employee", departments: [] });
  const [status, setStatus] = useState("");

  const loadUsers = async () => {
    const res = await fetch(`${API}/admin/users`, { headers: authHeader });
    if (res.ok) setUsers(await res.json());
  };

  useEffect(() => { loadUsers(); }, []);

  const toggleDept = (list, dept) =>
    list.includes(dept) ? list.filter((d) => d !== dept) : [...list, dept];

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/admin/users`, {
        method: "POST",
        headers: { ...authHeader, "Content-Type": "application/json" },
        body: JSON.stringify(newUser),
      });
      if (!res.ok) throw new Error();
      setStatus(`✅ User ${newUser.username} created`);
      setNewUser({ username: "", password: "", role: "employee", departments: [] });
      loadUsers();
    } catch {
      setStatus("⚠️ Could not create user (maybe exists already).");
    }
  };

  const handleUpdateDepartments = async (username, departments) => {
    await fetch(`${API}/admin/users/${username}/departments`, {
      method: "PUT",
      headers: { ...authHeader, "Content-Type": "application/json" },
      body: JSON.stringify({ departments }),
    });
    loadUsers();
  };

  return (
    <>
      <div className="panel-card">
        <h3>Create a new user</h3>
        <form className="user-form" onSubmit={handleCreateUser}>
          <input placeholder="Username" value={newUser.username} onChange={(e) => setNewUser({ ...newUser, username: e.target.value })} required />
          <input placeholder="Password" type="password" value={newUser.password} onChange={(e) => setNewUser({ ...newUser, password: e.target.value })} required />
          <select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}>
            <option value="employee">Employee</option>
            <option value="admin">Admin</option>
          </select>
          <div className="dept-checkboxes">
            {DEPARTMENTS.map((d) => (
              <label key={d}>
                <input
                  type="checkbox"
                  checked={newUser.departments.includes(d)}
                  onChange={() => setNewUser({ ...newUser, departments: toggleDept(newUser.departments, d) })}
                />
                {d}
              </label>
            ))}
          </div>
          <button type="submit" className="primary-btn">Create User</button>
        </form>
        {status && <p className="status-msg">{status}</p>}
      </div>

      <div className="panel-card">
        <h3>Users</h3>
        <table className="admin-table">
          <thead>
            <tr><th>Username</th><th>Role</th><th>Departments</th></tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.username}>
                <td>{u.username}</td>
                <td><span className="badge">{u.role}</span></td>
                <td>
                  <div className="dept-checkboxes inline">
                    {DEPARTMENTS.map((d) => (
                      <label key={d}>
                        <input
                          type="checkbox"
                          checked={u.departments.includes(d)}
                          onChange={() => handleUpdateDepartments(u.username, toggleDept(u.departments, d))}
                        />
                        {d}
                      </label>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default AdminDashboard;