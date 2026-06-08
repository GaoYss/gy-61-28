import { useMemo, useState } from "react";

import { AppShell } from "./components/AppShell";
import { AlarmCenter } from "./modules/alarms/AlarmCenter";
import { Dashboard } from "./modules/dashboard/Dashboard";
import { DeviceManagement } from "./modules/devices/DeviceManagement";
import { DoorLogSearch } from "./modules/logs/DoorLogSearch";
import { VisitorRecords } from "./modules/visitors/VisitorRecords";
import { useAccessData } from "./hooks/useAccessData";

export default function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const accessData = useAccessData();

  const content = useMemo(() => {
    const props = { data: accessData };
    const views = {
      dashboard: <Dashboard {...props} />,
      devices: <DeviceManagement {...props} />,
      visitors: <VisitorRecords {...props} />,
      alarms: <AlarmCenter {...props} />,
      logs: <DoorLogSearch {...props} />,
    };
    return views[activeView] || views.dashboard;
  }, [accessData, activeView]);

  return (
    <AppShell activeView={activeView} onChangeView={setActiveView}>
      {content}
    </AppShell>
  );
}
