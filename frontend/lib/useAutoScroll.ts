"use client";

import { useEffect, useRef } from "react";

/**
 * Auto-scrolls a container to the bottom when new items are appended.
 * Returns a ref to attach to a sentinel element at the bottom of the list.
 */
export function useAutoScroll(deps: unknown[]) {
  const endRef = useRef<HTMLDivElement>(null);
  const countRef = useRef(0);

  useEffect(() => {
    const currentCount =
      Array.isArray(deps[0]) ? (deps[0] as unknown[]).length : 0;
    // Only scroll when count *increases* (not on initial load or deletion)
    if (currentCount > countRef.current && countRef.current > 0) {
      endRef.current?.scrollIntoView({ behavior: "smooth" });
    }
    countRef.current = currentCount;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return endRef;
}
