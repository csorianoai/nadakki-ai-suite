import React from "react";

const styles = {
  active: "bg-green-100 text-green-700", expired: "bg-yellow-100 text-yellow-700",
  draft: "bg-gray-100 text-gray-700", scheduled: "bg-blue-100 text-blue-700",
  published: "bg-green-100 text-green-700", failed: "bg-red-100 text-red-700"
};

export default function StatusBadge({ status, label }) {
  return <span className={`px-2 py-1 text-xs font-medium rounded-full ${styles[status] || "bg-gray-100"}`}>{label || status}</span>;
}
