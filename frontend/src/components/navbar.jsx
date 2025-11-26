import React, { useState } from "react";
import "../components-css/navbar.css";

export default function Navbar({ onAccountClick = () => {} }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const userName = "Test User";
  const initials = userName
    .split(" ")
    .map((s) => s[0] || "")
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <header className="nav">
  <div className="nav-container">

    {/* LEFT */}
    <div className="nav-left">
      <div className="nav-logo">
        <span className="logo-mark">AI</span>
        <span className="logo-text">Consortium</span>
      </div>
    </div>

    {/* CENTER */}
    <div className="nav-center">
      <nav className={`nav-links ${menuOpen ? "open" : ""}`}>
        <a href="/">Home</a>
        <a href="/upload">Analysis</a>
        <a href="/feedback">Feedback</a>
        <a href="/cht">Interview Prep</a>
      </nav>
    </div>

    {/* RIGHT */}
    <div className="nav-right">
      <button className="btn-primary">Sign in</button>

      <button
        className="nav-avatar-btn"
        aria-label="Open account"
        onClick={(e) => {
          e.stopPropagation();
          onAccountClick();
        }}
      >
        <span className="nav-avatar">{initials}</span>
      </button>

      <button
        className="nav-toggle"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((s) => !s)}
      >
        <span className="hamburger" />
      </button>
    </div>

  </div>
</header>

  );
}
