import { useEffect, useMemo, useState } from "react";

import { accessApi } from "../api/client";

export function useAccessData() {
  const [state, setState] = useState({
    loading: true,
    error: "",
    stats: null,
    devices: [],
    visitors: [],
    alarms: [],
    logs: [],
  });

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const [stats, devices, visitors, alarms, logs] = await Promise.all([
          accessApi.stats(),
          accessApi.devices(),
          accessApi.visitors(),
          accessApi.alarms(),
          accessApi.doorLogs(),
        ]);
        if (mounted) {
          setState({ loading: false, error: "", stats, devices, visitors, alarms, logs });
        }
      } catch (error) {
        if (mounted) {
          setState((current) => ({ ...current, loading: false, error: error.message }));
        }
      }
    }

    load();
    return () => {
      mounted = false;
    };
  }, []);

  return useMemo(() => state, [state]);
}
