import React from "react";
import { Link } from "react-router-dom";

export default function ProfileCard({ user }) {
  return (
    <div className="flex flex-row gap-10">
        <div className="bg-green-50 w-1/2 rounded-xl  p-6 flex flex-col md:flex-row items-center shadow-md">
          {/* Avatar with Edit Button Overlay */}
          <div className="relative mr-6">
            <img
              src={user.avatarUrl || "/default-avatar.png"}
              alt="Profile"
              className="w-20 h-20 rounded-full object-cover border-4 border-white shadow"
            />
            <Link
              to="/settings"
              className="absolute bottom-0 right-0 bg-red-500 text-white rounded-full p-2 shadow hover:bg-red-600 transition flex items-center justify-center"
              style={{ width: "36px", height: "36px" }}
              title="Edit Profile"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                fill="none"
                viewBox="0 0 24 24"
              >
                <path
                  fill="currentColor"
                  d="M3 17.25V21h3.75l11.06-11.06-3.75-3.75L3 17.25zm17.71-10.04a1.003 1.003 0 0 0 0-1.42l-2.5-2.5a1.003 1.003 0 0 0-1.42 0l-1.83 1.83 3.75 3.75 1.83-1.83z"
                />
              </svg>
            </Link>
          </div>
          {/* User Info */}
          <div className="flex-1">
            <h2 className="text-xl font-bold mb-2">General</h2>
            <div className="space-y-1 text-gray-700">
              <div>
                <span className="font-semibold">Name:</span> {user.profilename}
              </div>
              <div>
                <span className="font-semibold">Email:</span> {user.email}
              </div>
              <div>
                <span className="font-semibold">Phone:</span> {user.phone}
              </div>
              <div>
                <span className="font-semibold">Birthday:</span> {user.birthday}
              </div>
              <div>
                <span className="font-semibold">Address:</span> {user.address}
              </div>
            </div>
          </div>
          
        </div>
        <div className="bg-[#85c3d1]rounded-xl w-1/2  p-6 flex flex-col md:flex-row items-center shadow-md"> 
            <div className="flex-1">
           <h2 className="text-xl font-bold mb-2">Yet can't find what you're looking for?</h2> 
            <div className="space-y-1 text-gray-500">
              <div>
                <span className="font-semibold text-4xl">Call us:</span> (60) 305-240-9671
              </div>
            </div>
          </div>
        </div>
    </div>
  );
}