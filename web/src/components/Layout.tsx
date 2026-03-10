import { NavLink, Outlet } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Health" },
  { to: "/hits", label: "Hits" },
  { to: "/opportunities", label: "Opportunities" },
  { to: "/recent", label: "Recent" },
];

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      <nav className="flex w-56 flex-col border-r border-gray-800 bg-gray-900 p-4">
        <h1 className="mb-6 text-lg font-bold text-white">PBS Wisconsin</h1>
        <ul className="space-y-1">
          {NAV_ITEMS.map(({ to, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  `block rounded-md px-3 py-2 text-sm ${
                    isActive
                      ? "bg-gray-800 text-white font-medium"
                      : "text-gray-400 hover:bg-gray-800 hover:text-white"
                  }`
                }
              >
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <main className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
