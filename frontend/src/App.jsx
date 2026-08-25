import { useState } from "react";
import { registerUser, loginUser, getCurrentUser } from "./api";

function App() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [currentUser, setCurrentUser] = useState(null);
  const [message, setMessage] = useState("");

  async function handleRegister(event) {
    event.preventDefault();

    try {
      const user = await registerUser(email, username, password);
      setMessage(`Registered user: ${user.username}`);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleLogin(event) {
    event.preventDefault();

    try {
      const data = await loginUser(username, password);
      localStorage.setItem("token", data.access_token);
      setMessage("Logged in successfully");
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleGetMe() {
    try {
      const user = await getCurrentUser();
      setCurrentUser(user);
      setMessage("Fetched current user");
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <div>
      <h1>Training Tracker</h1>

      <form onSubmit={handleRegister}>
        <h2>Register</h2>

        <input
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />

        <input
          placeholder="Username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />

        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />

        <button type="submit">Register</button>
      </form>

      <form onSubmit={handleLogin}>
        <h2>Login</h2>

        <input
          placeholder="Username or email"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />

        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />

        <button type="submit">Login</button>
      </form>

      <button onClick={handleGetMe}>Get Current User</button>

      {message && <p>{message}</p>}

      {currentUser && (
        <div>
          <h2>Current User</h2>
          <p>ID: {currentUser.id}</p>
          <p>Email: {currentUser.email}</p>
          <p>Username: {currentUser.username}</p>
        </div>
      )}
    </div>
  );
}

export default App;