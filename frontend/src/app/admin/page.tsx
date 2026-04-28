"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Agent {
  id: number;
  name: string;
  role: string;
  sprite_id: string;
}

interface LLMConfig {
  ollama_api_base: string;
  nvidia_api_base: string;
  has_nvidia_key: boolean;
}

export default function AdminPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [models, setModels] = useState<string[]>([]);
  const [currentModel, setCurrentModel] = useState<string>("");
  const [config, setConfig] = useState<LLMConfig>({
    ollama_api_base: "",
    nvidia_api_base: "",
    has_nvidia_key: false
  });
  const [nvidiaKey, setNvidiaKey] = useState("");
  const [formData, setFormData] = useState({
    name: "",
    role: "",
    sprite_id: "agent_1",
    efficiency: 50,
    creativity: 50,
    grumpiness: 50,
    loyalty: 50
  });

  useEffect(() => {
    // Fetch Agents
    fetch("http://localhost:8080/api/agents")
      .then(res => res.json())
      .then(data => setAgents(data))
      .catch(e => console.error(e));

    // Fetch LLM Models
    fetch("http://localhost:8080/api/llm/models")
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setModels(data);
      })
      .catch(e => console.error(e));

    // Fetch Current LLM
    fetch("http://localhost:8080/api/llm/current")
      .then(res => res.json())
      .then(data => {
        if (data.model) setCurrentModel(data.model);
      })
      .catch(e => console.error(e));

    // Fetch Config
    fetch("http://localhost:8080/api/llm/config")
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(e => console.error(e));
  }, []);

  const handleModelChange = async (newModel: string) => {
    try {
      const res = await fetch("http://localhost:8080/api/llm/current", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: newModel })
      });
      if (res.ok) {
        setCurrentModel(newModel);
        alert("LLM Model Updated!");
      }
    } catch (e) {
      console.error(e);
      alert("Error updating model");
    }
  };

  const saveConfig = async () => {
    try {
      const res = await fetch("http://localhost:8080/api/llm/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ollama_api_base: config.ollama_api_base,
          nvidia_api_base: config.nvidia_api_base,
          nvidia_api_key: nvidiaKey
        })
      });
      if (res.ok) {
        alert("Configuration Saved!");
        setNvidiaKey("");
        // Refresh config
        const configRes = await fetch("http://localhost:8080/api/llm/config");
        const configData = await configRes.json();
        setConfig(configData);
      }
    } catch (e) {
      console.error(e);
      alert("Error saving configuration");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:8080/api/agents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        const newAgent = await res.json();
        setAgents([...agents, newAgent]);
        alert("Agent Created Successfully!");
        setFormData({ ...formData, name: "", role: "" });
      }
    } catch (e) {
      console.error(e);
      alert("Error creating agent");
    }
  };

  return (
    <main className="min-h-screen bg-[#1a1c2c] p-8 text-white flex flex-col items-center">
      <div className="w-full max-w-6xl flex justify-between items-center mb-8">
        <h1 className="nes-text is-primary text-3xl uppercase">Admin Dashboard</h1>
        <Link href="/" className="nes-btn uppercase !text-lg">Back to Office</Link>
      </div>

      <div className="w-full max-w-6xl flex flex-col gap-8">
        <div className="flex gap-8">
          {/* LLM Configuration Section */}
          <div className="nes-container is-dark with-title flex-1">
            <p className="title text-[#f4b41b] !text-lg uppercase">LLM Engine Selection</p>
            <div className="flex flex-col gap-4 p-4 bg-black border border-gray-600 rounded">
              <label className="text-sm uppercase font-bold text-gray-400">Active Model:</label>
              <div className="nes-select is-dark !w-full">
                <select 
                  className="!text-lg"
                  value={currentModel} 
                  onChange={e => handleModelChange(e.target.value)}
                >
                  <option value="" disabled>Select a model...</option>
                  {models.map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
              <p className="text-xs text-gray-500 mt-2 italic">Current: {currentModel}</p>
            </div>
          </div>

          {/* Provider Settings */}
          <div className="nes-container is-dark with-title flex-1">
            <p className="title text-[#3498db] !text-lg uppercase">Provider Settings</p>
            <div className="flex flex-col gap-4">
              <div className="nes-field">
                <label className="!text-sm uppercase font-bold">Ollama API Base</label>
                <input 
                  type="text" 
                  className="nes-input is-dark !text-sm" 
                  value={config.ollama_api_base}
                  onChange={e => setConfig({...config, ollama_api_base: e.target.value})}
                />
              </div>
              <div className="nes-field">
                <label className="!text-sm uppercase font-bold">NVIDIA NIM Base</label>
                <input 
                  type="text" 
                  className="nes-input is-dark !text-sm" 
                  value={config.nvidia_api_base}
                  onChange={e => setConfig({...config, nvidia_api_base: e.target.value})}
                />
              </div>
              <div className="nes-field">
                <label className="!text-sm uppercase font-bold">NVIDIA API Key</label>
                <input 
                  type="password" 
                  className="nes-input is-dark !text-sm" 
                  placeholder={config.has_nvidia_key ? "******** (Already set)" : "Enter API Key..."}
                  value={nvidiaKey}
                  onChange={e => setNvidiaKey(e.target.value)}
                />
              </div>
              <button onClick={saveConfig} className="nes-btn is-primary uppercase !text-sm">Save Config</button>
            </div>
          </div>
        </div>

        <div className="flex gap-8">
          {/* Create Agent Form */}
          <div className="nes-container is-dark with-title w-1/2">
            <p className="title text-[#5cce84] !text-lg uppercase">Forge New Soul</p>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div className="nes-field">
                <label htmlFor="name_field" className="!text-sm uppercase font-bold">Agent Name</label>
                <input type="text" id="name_field" className="nes-input is-dark !text-lg" required 
                  value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
              </div>
              
              <div className="nes-field">
                <label htmlFor="role_field" className="!text-sm uppercase font-bold">Role</label>
                <input type="text" id="role_field" className="nes-input is-dark !text-lg" required 
                  value={formData.role} onChange={e => setFormData({...formData, role: e.target.value})} />
              </div>

              <div className="mt-4">
                <label className="!text-sm uppercase font-bold">Personality Traits</label>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm">Efficiency:</span>
                  <input type="range" className="w-1/2" min="0" max="100" value={formData.efficiency} 
                    onChange={e => setFormData({...formData, efficiency: parseInt(e.target.value)})} />
                </div>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm">Creativity:</span>
                  <input type="range" className="w-1/2" min="0" max="100" value={formData.creativity} 
                    onChange={e => setFormData({...formData, creativity: parseInt(e.target.value)})} />
                </div>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm">Grumpiness:</span>
                  <input type="range" className="w-1/2" min="0" max="100" value={formData.grumpiness} 
                    onChange={e => setFormData({...formData, grumpiness: parseInt(e.target.value)})} />
                </div>
              </div>

              <button type="submit" className="nes-btn is-success mt-4 uppercase !text-lg">Instantiate Agent</button>
            </form>
          </div>

          {/* Existing Agents */}
          <div className="nes-container is-dark with-title w-1/2">
            <p className="title text-[#5b6ee1] !text-lg uppercase">Active Roster</p>
            <div className="flex flex-col gap-4">
              {agents.map(a => (
                <div key={a.id} className="p-4 border border-gray-600 bg-black flex justify-between items-center">
                  <div>
                    <div className="font-bold text-lg">{a.name}</div>
                    <div className="text-sm text-gray-400">{a.role}</div>
                  </div>
                  <button className="nes-btn is-error text-sm p-2 uppercase">Delete</button>
                </div>
              ))}
              {agents.length === 0 && <p className="text-sm text-gray-500">No agents registered.</p>}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
