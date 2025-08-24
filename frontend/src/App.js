import React, { useState } from "react";
import axios from "axios";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:8000/search?query=${query}`);
      setResults(response.data.results || []);
    } catch (err) {
      console.error("Search error:", err);
      setResults([]);
    }
    setLoading(false);
  };

  return (
    <div style={{ fontFamily: "Arial, sans-serif", padding: "20px", maxWidth: "800px", margin: "auto" }}>
      <h2 style={{ textAlign: "center", marginBottom: "20px" }}>🔍 DSA Search Engine</h2>

      <div style={{ display: "flex", marginBottom: "20px" }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search DSA problems (e.g. dp, graph, greedy)..."
          style={{
            flex: 1,
            padding: "10px",
            fontSize: "16px",
            border: "1px solid #ccc",
            borderRadius: "5px",
          }}
        />
        <button
          onClick={handleSearch}
          style={{
            marginLeft: "10px",
            padding: "10px 20px",
            fontSize: "16px",
            border: "none",
            backgroundColor: "#007bff",
            color: "white",
            borderRadius: "5px",
            cursor: "pointer",
          }}
        >
          Search
        </button>
      </div>

      {loading && <p>Loading...</p>}

      {results.length > 0 ? (
        <div>
          {results.map((item, index) => (
            <div
              key={index}
              style={{
                border: "1px solid #ddd",
                padding: "15px",
                marginBottom: "15px",
                borderRadius: "8px",
                boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
              }}
            >
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ fontSize: "18px", fontWeight: "bold", color: "#007bff", textDecoration: "none" }}
              >
                {item.title}
              </a>
              <div style={{ marginTop: "8px" }}>
                {item.tags && item.tags.length > 0 ? (
                  item.tags.map((tag, i) => (
                    <span
                      key={i}
                      style={{
                        display: "inline-block",
                        backgroundColor: "#f1f1f1",
                        color: "#333",
                        padding: "4px 8px",
                        marginRight: "6px",
                        borderRadius: "5px",
                        fontSize: "13px",
                      }}
                    >
                      {tag}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: "13px", color: "#888" }}>No tags</span>
                )}
              </div>
              <p style={{ fontSize: "12px", color: "#666", marginTop: "8px" }}>
                Similarity: {(item.similarity * 100).toFixed(2)}%
              </p>
            </div>
          ))}
        </div>
      ) : (
        !loading && <p>No results found.</p>
      )}
    </div>
  );
}

export default App;
