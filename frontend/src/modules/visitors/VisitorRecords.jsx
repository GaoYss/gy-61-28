import { CalendarClock, Phone, UserRound } from "lucide-react";

import { EmptyState } from "../../components/EmptyState";
import { StatusBadge } from "../../components/StatusBadge";
import { formatDateTime } from "../../utils/format";

export function VisitorRecords({ data }) {
  return (
    <section className="view-stack">
      <header className="page-header">
        <div>
          <h1>访客通行记录</h1>
          <p>跟踪访客预约、审批状态、拜访对象和授权门禁。</p>
        </div>
      </header>

      <div className="record-grid">
        {data.visitors.map((visitor) => (
          <article className="record-card" key={visitor.id}>
            <div className="record-card-head">
              <strong><UserRound size={17} />{visitor.visitor_name}</strong>
              <StatusBadge value={visitor.pass_status} label={visitor.pass_status_display} />
            </div>
            <p>{visitor.reason}</p>
            <dl>
              <div><dt>受访人</dt><dd>{visitor.host_name}</dd></div>
              <div><dt>门禁</dt><dd>{visitor.device_name}</dd></div>
              <div><dt><Phone size={14} />电话</dt><dd>{visitor.phone}</dd></div>
              <div><dt><CalendarClock size={14} />到访</dt><dd>{formatDateTime(visitor.visit_time)}</dd></div>
            </dl>
          </article>
        ))}
      </div>
      {!data.visitors.length && <EmptyState />}
    </section>
  );
}
