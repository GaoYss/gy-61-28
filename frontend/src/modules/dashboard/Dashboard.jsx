import { AlertTriangle, CheckCircle2, Clock3, Router, UsersRound } from "lucide-react";

import { EmptyState } from "../../components/EmptyState";
import { MetricCard } from "../../components/MetricCard";
import { StatusBadge } from "../../components/StatusBadge";
import { formatDateTime } from "../../utils/format";

export function Dashboard({ data }) {
  if (data.loading) return <section className="panel">数据加载中...</section>;
  if (data.error) return <section className="panel error-panel">{data.error}</section>;

  const latestAlarms = data.alarms.slice(0, 3);
  const latestLogs = data.logs.slice(0, 5);

  return (
    <section className="view-stack">
      <header className="page-header">
        <div>
          <h1>小区智能门禁运行总览</h1>
          <p>集中查看设备在线、访客预约、异常告警和今日开门结果。</p>
        </div>
      </header>

      <div className="metrics-grid">
        <MetricCard label="门禁设备" value={data.stats.devices_total} tone="blue" />
        <MetricCard label="在线设备" value={data.stats.devices_online} tone="green" />
        <MetricCard label="待审批访客" value={data.stats.visitors_pending} tone="amber" />
        <MetricCard label="未处理告警" value={data.stats.open_alarms} tone="red" />
        <MetricCard label="今日成功开门" value={data.stats.today_success_logs} tone="teal" />
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-title">
            <AlertTriangle size={18} />
            <h2>最新异常</h2>
          </div>
          {latestAlarms.length ? (
            <div className="compact-list">
              {latestAlarms.map((alarm) => (
                <div className="compact-row" key={alarm.id}>
                  <div>
                    <strong>{alarm.title}</strong>
                    <span>{alarm.device_name} · {formatDateTime(alarm.occurred_at)}</span>
                  </div>
                  <StatusBadge value={alarm.level} label={alarm.level_display} />
                </div>
              ))}
            </div>
          ) : (
            <EmptyState />
          )}
        </div>

        <div className="panel">
          <div className="panel-title">
            <Clock3 size={18} />
            <h2>实时开门流水</h2>
          </div>
          {latestLogs.length ? (
            <div className="timeline">
              {latestLogs.map((log) => (
                <div className="timeline-row" key={log.id}>
                  {log.result === "success" ? <CheckCircle2 size={17} /> : <UsersRound size={17} />}
                  <div>
                    <strong>{log.opener_name}</strong>
                    <span>{log.device_name} · {log.credential_method_display} · {formatDateTime(log.opened_at)}</span>
                  </div>
                  <StatusBadge value={log.result} label={log.result_display} />
                </div>
              ))}
            </div>
          ) : (
            <EmptyState />
          )}
        </div>
      </div>

      <div className="panel">
        <div className="panel-title">
          <Router size={18} />
          <h2>通行方式统计</h2>
        </div>
        <div className="method-bars">
          {data.stats.logs_by_method.map((item) => (
            <div className="method-row" key={item.credential_method}>
              <span>{item.credential_method}</span>
              <div>
                <i style={{ width: `${Math.max(item.count * 24, 12)}px` }} />
              </div>
              <strong>{item.count}</strong>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
