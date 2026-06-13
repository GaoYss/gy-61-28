import { Download, Search } from "lucide-react";
import { useMemo, useState } from "react";

import { accessApi } from "../../api/client";
import { EmptyState } from "../../components/EmptyState";
import { StatusBadge } from "../../components/StatusBadge";
import { formatDateTime } from "../../utils/format";

export function DoorLogSearch({ data }) {
  const [keyword, setKeyword] = useState("");
  const [result, setResult] = useState("");
  const [openerType, setOpenerType] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [exporting, setExporting] = useState(false);

  const logs = useMemo(() => {
    return data.logs.filter((log) => {
      const matchesKeyword = keyword
        ? `${log.opener_name}${log.device_name}${log.failure_reason}`.toLowerCase().includes(keyword.toLowerCase())
        : true;
      const matchesResult = result ? log.result === result : true;
      const matchesOpenerType = openerType ? log.opener_type === openerType : true;
      const matchesStartTime = startTime ? new Date(log.opened_at) >= new Date(startTime) : true;
      const matchesEndTime = endTime ? new Date(log.opened_at) <= new Date(endTime + "T23:59:59") : true;
      return matchesKeyword && matchesResult && matchesOpenerType && matchesStartTime && matchesEndTime;
    });
  }, [data.logs, keyword, result, openerType, startTime, endTime]);

  async function handleExport() {
    try {
      setExporting(true);
      const filters = {};
      if (keyword) filters.keyword = keyword;
      if (result) filters.result = result;
      if (openerType) filters.opener_type = openerType;
      if (startTime) filters.start_time = startTime;
      if (endTime) filters.end_time = endTime + "T23:59:59";
      const blob = await accessApi.exportDoorLogs(filters);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `开门日志_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      alert(error.message || "导出失败");
    } finally {
      setExporting(false);
    }
  }

  return (
    <section className="view-stack">
      <header className="page-header">
        <div>
          <h1>开门日志查询</h1>
          <p>按人员、设备、时间和开门结果快速筛选门禁流水。</p>
        </div>
        <button className="btn-primary" onClick={handleExport} disabled={exporting}>
          <Download size={16} />
          {exporting ? "导出中..." : "导出日志"}
        </button>
      </header>

      <div className="filter-bar">
        <label>
          <Search size={16} />
          <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜索人员、设备或原因" />
        </label>
        <select value={openerType} onChange={(event) => setOpenerType(event.target.value)}>
          <option value="">全部类型</option>
          <option value="resident">业主</option>
          <option value="visitor">访客</option>
          <option value="admin">管理员</option>
          <option value="system">系统</option>
        </select>
        <select value={result} onChange={(event) => setResult(event.target.value)}>
          <option value="">全部结果</option>
          <option value="success">成功</option>
          <option value="denied">拒绝</option>
        </select>
        <input
          type="date"
          value={startTime}
          onChange={(event) => setStartTime(event.target.value)}
          placeholder="开始日期"
        />
        <input
          type="date"
          value={endTime}
          onChange={(event) => setEndTime(event.target.value)}
          placeholder="结束日期"
        />
      </div>

      <div className="table-panel">
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>人员</th>
              <th>类型</th>
              <th>设备</th>
              <th>方式</th>
              <th>结果</th>
              <th>说明</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{formatDateTime(log.opened_at)}</td>
                <td>{log.opener_name}</td>
                <td>{log.opener_type_display}</td>
                <td>{log.device_name}</td>
                <td>{log.credential_method_display}</td>
                <td><StatusBadge value={log.result} label={log.result_display} /></td>
                <td>{log.failure_reason || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!logs.length && <EmptyState />}
      </div>
    </section>
  );
}
