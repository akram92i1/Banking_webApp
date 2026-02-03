import React, { useState, useRef } from "react";
import ApiTester from './ApiTester';
import { useAuth } from '../contexts/AuthContext';

const initialProfile = {
  name: "John Doe",
  email: "Johndoe@gmail.com",
  avatar: "/avatar-john.png", // Replace with your default avatar path
};

export default function Settings() {
  const [activeTab, setActiveTab] = useState("profile");
  const [profile, setProfile] = useState(initialProfile);
  const [avatarPreview, setAvatarPreview] = useState(profile.avatar);
  const fileInputRef = useRef();

  const handleTabClick = (tab) => setActiveTab(tab);

  const handleInputChange = (e) => {
    setProfile({ ...profile, [e.target.name]: e.target.value });
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAvatarPreview(URL.createObjectURL(file));
      // You can also handle file upload here
    }
  };

  const handleReset = () => {
    setProfile(initialProfile);
    setAvatarPreview(initialProfile.avatar);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleUpdate = (e) => {
    e.preventDefault();
    // Handle update logic (API call, etc.)
    alert("Profile updated!");
  };

  return (
    <div className="flex flex-row gap-x-8 p-8 max-w-7xl mx-auto">
      {/* Left: Settings Card */}
      <div className="glass-card rounded-3xl p-8 flex-1 max-w-xl border border-white/10">
        {/* Tabs */}
        <div className="flex border-b border-white/10 mb-6">
          {["profile", "password", "notification"].map((tab) => (
            <button
              key={tab}
              className={`px-4 py-2 font-semibold capitalize border-b-2 transition ${activeTab === tab
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-glass-muted hover:text-glass"
                }`}
              onClick={() => handleTabClick(tab)}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "profile" && (
          <form onSubmit={handleUpdate}>
            <h2 className="text-2xl font-bold mb-4 text-glass">User Profile</h2>
            <input
              type="text"
              name="name"
              value={profile.name}
              onChange={handleInputChange}
              className="glass-input block w-full mb-4 rounded-xl border border-white/10 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-glass"
              placeholder="Name"
            />
            <input
              type="email"
              name="email"
              value={profile.email}
              onChange={handleInputChange}
              className="glass-input block w-full mb-4 rounded-xl border border-white/10 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-glass"
              placeholder="Email"
            />
            <div className="flex items-center mb-6">
              <img
                src={avatarPreview}
                alt="Avatar"
                className="w-14 h-14 rounded-full object-cover mr-4 ring-2 ring-white/20"
              />
              <input
                type="file"
                accept="image/*"
                ref={fileInputRef}
                onChange={handleAvatarChange}
                className="block flex-1 rounded-xl border border-white/10 px-2 py-1 text-glass-muted file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
              />
            </div>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={handleReset}
                className="flex-1 glass-button border border-white/10 rounded-xl py-2 font-semibold hover:bg-white/10 text-glass-muted"
              >
                Reset
              </button>
              <button
                type="submit"
                className="flex-1 bg-blue-600 text-white rounded-xl py-2 font-semibold hover:bg-blue-700 shadow-lg shadow-blue-500/20"
              >
                Update
              </button>
            </div>
          </form>
        )}

        {activeTab === "password" && (
          <form className="mt-4">
            <h2 className="text-2xl font-bold mb-4 text-glass">Change Password</h2>
            <input
              type="password"
              name="currentPassword"
              className="glass-input block w-full mb-4 rounded-xl border border-white/10 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-glass"
              placeholder="Current Password"
            />
            <input
              type="password"
              name="newPassword"
              className="glass-input block w-full mb-4 rounded-xl border border-white/10 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-glass"
              placeholder="New Password"
            />
            <input
              type="password"
              name="confirmPassword"
              className="glass-input block w-full mb-6 rounded-xl border border-white/10 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-glass"
              placeholder="Confirm New Password"
            />
            <button
              type="submit"
              className="w-full bg-blue-600 text-white rounded-xl py-3 font-semibold hover:bg-blue-700 shadow-lg shadow-blue-500/20 transition-all"
            >
              Update Password
            </button>
          </form>
        )}

        {activeTab === "notification" && (
          <div className="mt-4 text-glass">
            <h2 className="text-2xl font-bold mb-4 text-glass">Notification Settings</h2>
            <div className="flex items-center mb-4">
              <input type="checkbox" id="emailNotif" className="mr-3 w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 bg-slate-700" />
              <label htmlFor="emailNotif" className="text-glass-muted">Email Notifications</label>
            </div>
            <div className="flex items-center mb-4">
              <input type="checkbox" id="smsNotif" className="mr-3 w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 bg-slate-700" />
              <label htmlFor="smsNotif" className="text-glass-muted">SMS Notifications</label>
            </div>
            <div className="flex items-center mb-4">
              <input type="checkbox" id="pushNotif" className="mr-3 w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 bg-slate-700" />
              <label htmlFor="pushNotif" className="text-glass-muted">Push Notifications</label>
            </div>
          </div>
        )}
      </div>

      {/* Right: Support Box and API Tester */}
      <div className="flex flex-col gap-6 min-w-[320px]">
        <div className="glass-card rounded-3xl p-8 h-fit flex flex-col items-start border border-white/10 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-blue-500/10"></div>
          <h2 className="text-xl font-bold mb-2 text-glass relative z-10">
            Still can't find what you looking for?
          </h2>
          <div className="mb-4 relative z-10 text-glass-muted">
            <span className="font-bold">Call us: </span>
            <span>(60) 305-240-9671</span>
          </div>
          <button className="relative z-10 border border-white/20 text-white rounded-xl px-6 py-2 font-semibold hover:bg-white/10 transition glass-button">
            Chat with us
          </button>
        </div>

        {/* API Tester */}
        <div className="glass-card rounded-3xl shadow-md p-6 border border-white/10">
          <ApiTester />
        </div>
      </div>
    </div>
  );
}