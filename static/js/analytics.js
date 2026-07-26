(() => {
  const d = window.analyticsData; if (!d || !window.Chart) return;
  const palette=['#2563eb','#8b5cf6','#16a34a','#f59e0b','#dc2626','#06b6d4','#64748b','#ec4899'];
  function chart(id, source, type='bar') { const canvas=document.getElementById(id); if (!canvas) return; new Chart(canvas,{type,data:{labels:source.labels,datasets:[{data:source.data,backgroundColor:palette,borderColor:'#2563eb',fill:type==='line'?false:undefined,tension:.35}]},options:{maintainAspectRatio:false,plugins:{legend:{display:type==='doughnut'}}}}); }
  chart('statusChart',d.status,'doughnut'); chart('timeChart',d.time,'line'); chart('atsChart',d.ats); chart('companiesChart',d.companies); chart('rolesChart',d.roles); chart('demandChart',d.demand); chart('missingChart',d.missing); chart('performanceChart',d.performance,'line');
})();
