(() => {
  const data = window.dashboardData;
  if (!data || !window.Chart) return;
  const status = document.getElementById('statusChart');
  if (status) new Chart(status, {type: 'doughnut', data: {labels: data.status.labels, datasets: [{data: data.status.data, backgroundColor: ['#64748b','#2563eb','#f59e0b','#8b5cf6','#16a34a','#dc2626','#94a3b8']} ]}, options: {plugins:{legend:{position:'bottom'}}, maintainAspectRatio:false}});
})();
