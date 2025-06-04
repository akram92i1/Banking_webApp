import React, { useState, useRef } from "react";

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
    <div className="flex flex-row gap-x-8 p-8">
      {/* Left: Settings Card */}
      <div className="bg-white rounded-xl shadow p-8 flex-1 max-w-xl">
        {/* Tabs */}
        <div className="flex border-b mb-6">
          {["profile", "password", "notification"].map((tab) => (
            <button
              key={tab}
              className={`px-4 py-2 font-semibold capitalize border-b-2 transition ${
                activeTab === tab
                  ? "border-red-500 text-red-500"
                  : "border-transparent text-gray-500"
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
            <h2 className="text-2xl font-bold mb-4">User Profile</h2>
            <input
              type="text"
              name="name"
              value={profile.name}
              onChange={handleInputChange}
              className="block w-full mb-4 rounded-full border px-4 py-2 focus:outline-none"
              placeholder="Name"
            />
            <input
              type="email"
              name="email"
              value={profile.email}
              onChange={handleInputChange}
              className="block w-full mb-4 rounded-full border px-4 py-2 focus:outline-none"
              placeholder="Email"
            />
            <div className="flex items-center mb-6">
              <img
                src={avatarPreview}
                alt="Avatar"
                className="w-14 h-14 rounded-full object-cover mr-4"
              />
              <input
                type="file"
                accept="image/*"
                ref={fileInputRef}
                onChange={handleAvatarChange}
                className="block flex-1 rounded-full border px-2 py-1"
              />
            </div>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={handleReset}
                className="flex-1 border border-gray-400 rounded-full py-2 font-semibold hover:bg-gray-100"
              >
                Reset
              </button>
              <button
                type="submit"
                className="flex-1 bg-blue-900 text-white rounded-full py-2 font-semibold hover:bg-blue-800"
              >
                Update
              </button>
            </div>
          </form>
        )}

        {activeTab === "password" && (
          <form className="mt-4">
            <h2 className="text-2xl font-bold mb-4">Change Password</h2>
            <input
              type="password"
              name="currentPassword"
              className="block w-full mb-4 rounded-full border px-4 py-2 focus:outline-none"
              placeholder="Current Password"
            />
            <input
              type="password"
              name="newPassword"
              className="block w-full mb-4 rounded-full border px-4 py-2 focus:outline-none"
              placeholder="New Password"
            />
            <input
              type="password"
              name="confirmPassword"
              className="block w-full mb-6 rounded-full border px-4 py-2 focus:outline-none"
              placeholder="Confirm New Password"
            />
            <button
              type="submit"
              className="w-full bg-blue-900 text-white rounded-full py-2 font-semibold hover:bg-blue-800"
            >
              Update Password
            </button>
          </form>
        )}

        {activeTab === "notification" && (
          <div className="mt-4">
            <h2 className="text-2xl font-bold mb-4">Notification Settings</h2>
            <div className="flex items-center mb-4">
              <input type="checkbox" id="emailNotif" className="mr-2" />
              <label htmlFor="emailNotif">Email Notifications</label>
            </div>
            <div className="flex items-center mb-4">
              <input type="checkbox" id="smsNotif" className="mr-2" />
              <label htmlFor="smsNotif">SMS Notifications</label>
            </div>
            <div className="flex items-center mb-4">
              <input type="checkbox" id="pushNotif" className="mr-2" />
              <label htmlFor="pushNotif">Push Notifications</label>
            </div>
          </div>
        )}
      </div>

      {/* Right: Support Box */}
      <div className="bg-cyan-200 rounded-lg p-8 h-fit flex flex-col items-start min-w-[320px]">
        <h2 className="text-xl font-bold mb-2">
          Still can’t find what you looking for?
        </h2>
        <div className="mb-4">
          <span className="font-bold">Call us: </span>
          <span>(60) 305-240-9671</span>
        </div>
        <button className="border border-white text-white rounded-full px-6 py-2 font-semibold hover:bg-cyan-300 transition">
          Chat with us
        </button>
      </div>
    </div>
  );
}