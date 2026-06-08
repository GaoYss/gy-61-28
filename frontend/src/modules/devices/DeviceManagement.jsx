import { Activity, MapPin } from "lucide-react";

import { EmptyState } from "../../components/EmptyState";
import { StatusBadge } from "../../components/StatusBadge";
import { formatDateTime } from "../../utils/format";

export function DeviceManagement({ data }) {
  return (
    <section className="view-stack">
      <header className="page-header">
        <div>
          <h1>门禁设备管理</h1>
          <p>查看各出入口设备状态、安装位置和最近心跳时间。</p>
        </div>
      </header>

      <div className="table-panel">
        <table>
          <thead>
            <tr>
              <th>设备编号</th>
              <th>设备名称</th>
              <th>位置</th>
              <th>状态</th>
              <th>最近心跳</th>
            </tr>
          </thead>
          <tbody>
            {data.devices.map((device) => (
              <tr key={device.id}>
                <td>{device.device_code}</td>
                <td><Activity size={15} />{device.name}</td>
                <td><MapPin size={15} />{device.location}</td>
                <td><StatusBadge value={device.status} label={device.status_display} /></td>
                <td>{formatDateTime(device.last_heartbeat)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!data.devices.length && <EmptyState />}
      </div>
    </section>
  );
}
