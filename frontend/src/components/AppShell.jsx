import { Bell, DoorOpen, FileSearch, LayoutDashboard, ShieldCheck, UsersRound } from "lucide-react";

const navItems = [
  { id: "dashboard", label: "运行总览", icon: LayoutDashboard },
  { id: "devices", label: "门禁设备", icon: ShieldCheck },
  { id: "visitors", label: "访客记录", icon: UsersRound },
  { id: "alarms", label: "异常报警", icon: Bell },
  { id: "logs", label: "开门日志", icon: FileSearch },
];

export function AppShell({ activeView, onChangeView, children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <DoorOpen size={28} />
          <div>
            <strong>智慧门禁</strong>
            <span>社区安防管理</span>
          </div>
        </div>
        <nav className="nav-list">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                className={`nav-item ${activeView === item.id ? "active" : ""}`}
                key={item.id}
                onClick={() => onChangeView(item.id)}
                type="button"
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
