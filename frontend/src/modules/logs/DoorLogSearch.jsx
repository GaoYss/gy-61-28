import { Search } from "lucide-react";
import { useMemo, useState } from "react";

import { EmptyState } from "../../components/EmptyState";
import { StatusBadge } from "../../components/StatusBadge";
import { formatDateTime } from "../../utils/format";

export function DoorLogSearch({ data }) {
  const [keyword, setKeyword] = useState("");
  const [result, setResult] = useState("");

  const logs = useMemo(() => {
    return data.logs.filter((log) => {
      const matchesKeyword = keyword
        ? `${log.opener_name}${log.device_name}${log.failure_reason}`.toLowerCase().includes(keyword.toLowerCase())
        : true;
      const matchesResult = result ? log.result === result : true;
      return matchesKeyword && matchesResult;
    });
  }, [data.logs, keyword, result]);

  return (
    <section className="view-stack">
      <header className="page-header">
        <div>
          <h1>开门日志查询</h1>
          <p>按人员、设备、失败原因和开门结果快速筛选门禁流水。</p>
        </div>
      </header>

      <div className="filter-bar">
        <label>
          <Search size={16} />
          <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜索人员、设备或原因" />
        </label>
        <select value={result} onChange={(event) => setResult(event.target.value)}>
          <option value="">全部结果</option>
          <option value="success">成功</option>
          <option value="denied">拒绝</option>
        </select>
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
